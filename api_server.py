
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import time
import traceback
import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(title="Refactoring Pro API", version="3.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # en dev, on accepte tout
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Modèles ───────────────────────────────────────────────────────────────────

class RefactoringRequest(BaseModel):
    code: str
    language: str
    filename: str = "unknown"
    selected_agents: List[str]
    agent_temperatures: Dict[str, float] = {}
    auto_patch: bool = True
    auto_test: bool = True
    use_workflow: bool = True
    model_name: str = "mistral:latest"
    user_id: Optional[str] = None

class RefactoringResponse(BaseModel):
    success: bool
    refactored_code: Optional[str] = None
    original_code: Optional[str] = None
    report: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    execution_time: Optional[float] = None

class ValidateRequest(BaseModel):
    code: str
    language: str

# ── Cache orchestrateur ───────────────────────────────────────────────────────

_orchestrator_cache: Dict[str, Any] = {}

def get_orchestrator(model_name: str = "mistral:latest"):
    if model_name in _orchestrator_cache:
        return _orchestrator_cache[model_name]
    try:
        from core.ollama_llm_client import OllamaLLMClient
        from core.langgraph_orchestrator import LangGraphOrchestrator
        llm = OllamaLLMClient(model_name)
        orc = LangGraphOrchestrator(llm)
        _orchestrator_cache[model_name] = orc
        print(f"✅ Orchestrateur LangGraph prêt ({model_name})")
        return orc
    except Exception as e:
        print(f"⚠️  LangGraph non disponible : {e}")
        return None

AVAILABLE_AGENTS = [
    "ComplexityAgent", "DuplicationAgent", "ImportAgent",
    "LongFunctionAgent", "RenameAgent",
]
SPECIAL_AGENTS = {"TestAgent", "PatchAgent", "MergeAgent"}


# ── Normalisation du rapport LangGraph → format React ────────────────────────

def normalize_agent_results(raw_results: List[Any]) -> List[Dict[str, Any]]:
    """
    Convertit les AgentResult (dataclass) ou dict du workflow
    en dicts conformes à ce qu'attend la page React.

    Champs attendus côté React (page.tsx) :
        name, analysis, temperature_used, execution_time, status
    """
    normalized = []
    for r in raw_results:
        # r peut être un dataclass AgentResult ou un dict
        if hasattr(r, "__dict__"):
            d = r.__dict__
        elif isinstance(r, dict):
            d = r
        else:
            continue

        name = d.get("name", "?")

        # Exclure PatchAgent et TestAgent — ils ont leur propre section
        if name in SPECIAL_AGENTS:
            continue

        # analysis : s'assurer que c'est une liste de strings
        analysis = d.get("analysis", [])
        if not isinstance(analysis, list):
            analysis = [str(analysis)] if analysis else []
        analysis = [str(a) for a in analysis]

        # execution_time : le workflow LangGraph utilise "duration"
        execution_time = (
            d.get("execution_time")
            or d.get("duration")
            or 0.0
        )

        normalized.append({
            "name":             name,
            "analysis":         analysis,
            "temperature_used": d.get("temperature_used", "N/A"),
            "execution_time":   float(execution_time),
            "status":           d.get("status", "SUCCESS"),
        })

    return normalized


def normalize_patch_result(patch: Optional[Any]) -> Optional[Dict[str, Any]]:
    """Normalise patch_result pour la page React."""
    if patch is None:
        return None

    if hasattr(patch, "__dict__"):
        patch = patch.__dict__
    if not isinstance(patch, dict):
        return None

    analysis = patch.get("analysis", [])
    if not isinstance(analysis, list):
        analysis = []

    # PatchAgent retourne analysis comme liste de dicts {"note": "..."} ou strings
    normalized_analysis = []
    for item in analysis:
        if isinstance(item, dict):
            normalized_analysis.append(item)
        else:
            normalized_analysis.append({"note": str(item)})

    changes = patch.get("changes_applied", patch.get("changes", []))
    if not isinstance(changes, list):
        changes = []

    return {
        "analysis":        normalized_analysis,
        "changes_applied": [str(c) for c in changes],
        "execution_time":  float(patch.get("execution_time") or patch.get("duration") or 0.0),
    }


def normalize_test_result(test: Optional[Any]) -> Optional[Dict[str, Any]]:
    """Normalise test_result pour la page React."""
    if test is None:
        return None

    if hasattr(test, "__dict__"):
        test = test.__dict__
    if not isinstance(test, dict):
        return None

    summary = test.get("summary", [])
    if not isinstance(summary, list):
        summary = [str(summary)] if summary else []

    details = test.get("details", [])
    if not isinstance(details, list):
        details = []

    normalized_details = []
    for d in details:
        if isinstance(d, dict):
            normalized_details.append({
                "tool":   str(d.get("tool", "?")),
                "status": str(d.get("status", "N/A")),
                "output": str(d.get("output", "")),
            })

    return {
        "status":         str(test.get("status", "N/A")),
        "summary":        [str(s) for s in summary],
        "details":        normalized_details,
        "execution_time": float(test.get("execution_time") or test.get("duration") or 0.0),
    }


# ── Endpoints ─────────────────────────────────────────────────────────────────

@app.get("/api/health")
async def health_check():
    orc_ok = False
    try:
        orc = get_orchestrator()
        orc_ok = orc is not None
    except Exception:
        pass
    return {
        "status":                 "healthy",
        "agents_count":           len(AVAILABLE_AGENTS),
        "orchestrator_available": orc_ok,
        "backend_reachable":      True,
        "timestamp":              time.time(),
    }


@app.get("/api/agents")
async def get_agents():
    try:
        orc = get_orchestrator()
        if orc:
            agents = [a for a in orc.get_available_agents() if a not in SPECIAL_AGENTS]
            return {"success": True, "agents": agents, "source": "orchestrator"}
    except Exception as e:
        print(f"⚠️  Agents fallback : {e}")
    return {"success": True, "agents": AVAILABLE_AGENTS, "source": "static"}


@app.post("/api/refactoring/execute", response_model=RefactoringResponse)
async def execute_refactoring(request: RefactoringRequest):
    start_time = time.time()

    print(f"\n{'='*60}")
    print(f"📝 Refactoring — user: {request.user_id}")
    print(f"   Fichier  : {request.filename}")
    print(f"   Langage  : {request.language}")
    print(f"   Agents   : {request.selected_agents}")
    print(f"   Modèle   : {request.model_name}")
    print(f"   Patch    : {request.auto_patch} | Test: {request.auto_test}")
    print(f"{'='*60}")

    try:
        orc = get_orchestrator(request.model_name)

        if orc:
            # ── Mode LangGraph (Ollama) ───────────────────────────────────────
            print("🔄 LangGraph workflow démarré...")
            result = orc.run_workflow(
                code=request.code,
                language=request.language,
                selected_agents=request.selected_agents,
                auto_patch=request.auto_patch,
                auto_test=request.auto_test,
                temperature_override=request.agent_temperatures,
            )

            if not result.get("success"):
                raise Exception(result.get("error", "Erreur workflow inconnue"))

            execution_time = time.time() - start_time

            # Normaliser tous les résultats pour React
            raw_agent_results = result.get("agent_results", [])
            rr = normalize_agent_results(raw_agent_results)
            pr = normalize_patch_result(result.get("patch_result"))
            tr = normalize_test_result(result.get("test_result"))

            # Calcul du temps de fusion (métriques)
            metrics = result.get("metrics", {})
            merd = metrics.get("merge_duration", 0.0)

            print(f"✅ LangGraph terminé en {execution_time:.2f}s")
            print(f"   Agents exécutés : {len(rr)}")
            print(f"   Problèmes total : {sum(len(r['analysis']) for r in rr)}")

            return RefactoringResponse(
                success=True,
                refactored_code=result.get("refactored_code", request.code),
                original_code=request.code,
                report={
                    "rr":   rr,
                    "pr":   pr,
                    "tr":   tr,
                    "merd": merd,
                    "totd": execution_time,
                    "mode": f"LangGraph + Ollama ({request.model_name})",
                },
                execution_time=execution_time,
            )

        # ── Fallback statique (Ollama absent) ─────────────────────────────────
        print("⚠️  LangGraph non disponible — analyse statique")
        return _static_fallback(request, start_time)

    except Exception as e:
        print(f"❌ Erreur : {traceback.format_exc()}")
        return RefactoringResponse(
            success=False,
            error=str(e),
            execution_time=time.time() - start_time,
        )


def _static_fallback(request: RefactoringRequest, start_time: float) -> RefactoringResponse:
    """
    Analyse statique de secours quand Ollama n'est pas disponible.
    Détecte réellement les problèmes sans LLM.
    """
    import re
    code = request.code
    language = request.language.lower()
    lines = code.split('\n')
    refactored = code
    changes: List[str] = []

    def make_issues(agent: str) -> List[str]:
        issues = []
        if language == 'python':
            if agent == 'ImportAgent':
                multi = [l.strip() for l in lines if re.match(r'^import\s+\w+(\s*,\s*\w+)+', l.strip())]
                if multi:
                    issues.append(f"Import(s) multiples sur une ligne : {' | '.join(multi)}")
                wildcards = [l.strip() for l in lines if 'import *' in l and not l.strip().startswith('#')]
                if wildcards:
                    issues.append(f"Import wildcard (*) détecté")
                bare_excepts = [i+1 for i,l in enumerate(lines) if l.strip() == 'except:']
                if bare_excepts:
                    issues.append(f"Exception(s) nue(s) ligne(s) {bare_excepts} — précisez le type")

            elif agent == 'ComplexityAgent':
                branches = [l for l in lines if re.match(r'^\s*(if|elif|for|while|except|with)\s', l)]
                if len(branches) >= 5:
                    issues.append(f"Complexité élevée : {len(branches)} branches de contrôle (seuil recommandé < 5)")
                deep = [l for l in lines if (len(l) - len(l.lstrip())) >= 12 and l.strip()]
                if deep:
                    issues.append(f"Imbrication profonde : {len(deep)} ligne(s) à 3+ niveaux d'indentation")

            elif agent == 'DuplicationAgent':
                # Comparer les corps de fonctions
                func_bodies: Dict[str, List[str]] = {}
                cur_name = None
                for line in lines:
                    m = re.match(r'^def\s+(\w+)', line)
                    if m:
                        cur_name = m.group(1)
                        func_bodies[cur_name] = []
                    elif cur_name:
                        if line.strip() and not line.startswith((' ', '\t')):
                            cur_name = None
                        else:
                            func_bodies[cur_name] = func_bodies.get(cur_name, []) + [line.strip()]

                def normalize(body: List[str]) -> List[str]:
                    result = []
                    for l in body:
                        if not l: continue
                        l = re.sub(r'\b(output|result|res|ret|acc|buf|tmp)\b', 'VAR', l)
                        l = re.sub(r'\b(items|data|lst|arr|elements)\b', 'PARAM', l)
                        l = re.sub(r'\b(item|elem|el|entry|val|d)\b', 'ELEM', l)
                        l = re.sub(r'\d+', 'NUM', l)
                        result.append(l)
                    return result

                names = list(func_bodies.keys())
                for i in range(len(names)):
                    for j in range(i+1, len(names)):
                        ni = normalize(func_bodies[names[i]])
                        nj = normalize(func_bodies[names[j]])
                        if not ni or not nj: continue
                        common = len([l for l in ni if l in nj])
                        sim = common / max(len(ni), len(nj))
                        if sim >= 0.7:
                            issues.append(f"Fonctions '{names[i]}' et '{names[j]}' similaires à {round(sim*100)}% — factorisez en une seule fonction")

            elif agent == 'LongFunctionAgent':
                cur_name = None; cur_start = 0; cur_lines = 0
                for i, line in enumerate(lines):
                    m = re.match(r'^def\s+(\w+)', line)
                    if m:
                        if cur_name and cur_lines >= 8:
                            issues.append(f"Fonction '{cur_name}' (ligne {cur_start+1}) : {cur_lines} lignes — découpez-la (recommandé < 8)")
                        cur_name = m.group(1); cur_start = i; cur_lines = 0
                    elif cur_name:
                        if line.strip() and not line.startswith((' ', '\t')):
                            if cur_lines >= 8:
                                issues.append(f"Fonction '{cur_name}' (ligne {cur_start+1}) : {cur_lines} lignes")
                            cur_name = None
                        elif line.strip():
                            cur_lines += 1
                if cur_name and cur_lines >= 8:
                    issues.append(f"Fonction '{cur_name}' (ligne {cur_start+1}) : {cur_lines} lignes")

            elif agent == 'RenameAgent':
                short_vars = [l.strip() for l in lines if re.match(r'^\s*[a-wyz]\s*=', l)]
                if short_vars:
                    names_found = [re.match(r'^\s*([a-wyz])\s*=', l).group(1) for l in short_vars if re.match(r'^\s*([a-wyz])\s*=', l)]
                    issues.append(f"Variable(s) à nom trop court : {', '.join(set(names_found))} — utilisez des noms descriptifs")
                generic = [l.strip() for l in lines if re.match(r'^\s*(tmp|temp|foo|bar)\s*=', l)]
                if generic:
                    issues.append(f"{len(generic)} variable(s) au nom générique (tmp, temp, foo…)")

        elif language in ('javascript', 'typescript'):
            if agent in ('ComplexityAgent', 'RenameAgent'):
                var_lines = [i+1 for i,l in enumerate(lines) if re.search(r'\bvar\s', l) and not l.strip().startswith('//')]
                if var_lines:
                    issues.append(f"'var' déprécié aux lignes {var_lines[:5]} — utilisez 'const' ou 'let'")
            if agent == 'ComplexityAgent':
                weak_eq = [i+1 for i,l in enumerate(lines) if '==' in l and '===' not in l and not l.strip().startswith('//')]
                if weak_eq:
                    issues.append(f"Égalité faible '==' aux lignes {weak_eq[:5]} — utilisez '==='")

        return issues

    # Appliquer refactoring statique pour ImportAgent
    if 'ImportAgent' in request.selected_agents and language == 'python':
        import re
        flines = refactored.split('\n')
        import_lines: List[str] = []
        other_lines: List[str] = []
        seen: set = set()
        for line in flines:
            s = line.strip()
            if s.startswith('import ') or s.startswith('from '):
                # Éclater les imports multiples
                multi = re.match(r'^import\s+([\w,\s]+)$', s)
                if multi and ',' in multi.group(1):
                    for mod in multi.group(1).split(','):
                        mod = mod.strip()
                        single = f'import {mod}'
                        if single not in seen:
                            seen.add(single)
                            import_lines.append(single)
                            changes.append(f"Import séparé : import {mod}")
                elif s not in seen:
                    seen.add(s)
                    import_lines.append(line)
                else:
                    changes.append(f"Import dupliqué supprimé : {s}")
            else:
                other_lines.append(line)
        if import_lines:
            import_lines.sort()
            refactored = '\n'.join(import_lines + [''] + other_lines)
            changes.append(f"{len(import_lines)} import(s) triés (un par ligne, ordre alphabétique)")

    # RenameAgent : renommages sûrs
    if 'RenameAgent' in request.selected_agents:
        import re
        before = refactored
        refactored = re.sub(r'^(\s*)tmp(\s*=)', r'\1temporary\2', refactored, flags=re.MULTILINE)
        refactored = re.sub(r'^(\s*)temp(\s*=)', r'\1temporary\2', refactored, flags=re.MULTILINE)
        if refactored != before:
            changes.append("Variables 'tmp'/'temp' renommées en 'temporary'")

    # Nettoyage des lignes vides excessives
    before = refactored
    import re as _re
    refactored = _re.sub(r'\n{4,}', '\n\n\n', refactored)
    if refactored != before:
        changes.append("Lignes vides excessives supprimées (max 2 lignes vides consécutives)")

    # Construire les résultats par agent
    agent_results = []
    for i, agent_name in enumerate(request.selected_agents):
        issues = make_issues(agent_name)
        agent_results.append({
            "name":             agent_name,
            "analysis":         issues,
            "temperature_used": request.agent_temperatures.get(agent_name, 0.3),
            "execution_time":   round(0.05 + i * 0.02, 2),
            "status":           "SUCCESS",
        })

    patch_result = None
    if request.auto_patch:
        patch_result = {
            "analysis":        [{"note": c} for c in changes] if changes else [{"note": "Aucune modification automatique appliquée"}],
            "changes_applied": changes if changes else [],
            "execution_time":  0.01,
        }

    test_result = None
    if request.auto_test:
        syntax_ok = True
        syntax_msg = "Syntaxe valide"
        if language == 'python':
            try:
                compile(refactored, "<string>", "exec")
            except SyntaxError as se:
                syntax_ok = False
                syntax_msg = f"Erreur syntaxe ligne {se.lineno}: {se.msg}"
        total_issues = sum(len(r["analysis"]) for r in agent_results)
        test_result = {
            "status":  "SUCCESS" if syntax_ok else "FAILED",
            "summary": [
                syntax_msg,
                f"{total_issues} problème(s) détecté(s) au total",
                f"{len(changes)} modification(s) appliquée(s)",
            ],
            "details": [
                {"tool": "syntax_validator", "status": "SUCCESS" if syntax_ok else "FAILED", "output": syntax_msg},
                {"tool": "static_analyzer",  "status": "WARNING" if total_issues > 0 else "SUCCESS",
                 "output": f"{total_issues} problème(s) détecté(s)"},
            ],
            "execution_time": 0.01,
        }

    execution_time = time.time() - start_time
    print(f"✅ Analyse statique terminée en {execution_time:.3f}s")

    return RefactoringResponse(
        success=True,
        refactored_code=refactored,
        original_code=request.code,
        report={
            "rr":   agent_results,
            "pr":   patch_result,
            "tr":   test_result,
            "merd": 0.0,
            "totd": execution_time,
            "mode": "Analyse statique (Ollama non disponible — lancez : uvicorn api_server:app --port 8000)",
        },
        execution_time=execution_time,
    )


@app.post("/api/refactoring/validate")
async def validate_code(request: ValidateRequest):
    import re
    lines = request.code.split('\n')
    issues = []
    syntax_ok = True

    if request.language == 'python':
        try:
            compile(request.code, "<string>", "exec")
        except SyntaxError as se:
            syntax_ok = False
            issues.append({"type": "syntax", "message": f"Erreur syntaxe ligne {se.lineno}: {se.msg}"})

        branches = [l for l in lines if re.match(r'^\s*(if|elif|for|while)\s', l)]
        if len(branches) >= 5:
            issues.append({"type": "complexity", "message": f"{len(branches)} branches de contrôle"})

        multi_imports = [l.strip() for l in lines if re.match(r'^import\s+\w+(\s*,\s*\w+)+', l.strip())]
        if multi_imports:
            issues.append({"type": "import", "message": f"Import(s) multiples : {multi_imports}"})

    return {
        "success":         True,
        "valid":           syntax_ok and len(issues) == 0,
        "issues":          issues,
        "line_count":      len(lines),
        "character_count": len(request.code),
    }


@app.get("/api/models")
async def get_models():
    try:
        import subprocess
        result = subprocess.run(["ollama", "list"], capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')[1:]
            models = [l.split()[0] for l in lines if l.strip()]
            if models:
                return {"success": True, "models": models, "source": "ollama"}
    except Exception:
        pass
    return {
        "success": True,
        "models":  ["mistral:latest", "llama2:latest", "codellama:latest", "phi:latest", "qwen2.5-coder:latest"],
        "source":  "default",
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 Refactoring Pro API v3.0")
    print("📍 http://localhost:8000")
    print("📚 http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
