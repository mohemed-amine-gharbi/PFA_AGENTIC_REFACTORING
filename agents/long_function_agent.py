from agents.base_agent import BaseAgent
import ast
import re
from typing import Optional, Dict, Any, List


class LongFunctionAgent(BaseAgent):
    """
    Agent qui détecte les fonctions trop longues via AST
    et propose un découpage en sous-fonctions cohérentes.
    """

    # Seuils de détection
    MAX_LINES        = 20
    MAX_STATEMENTS   = 15
    MAX_PARAMS       = 5
    MAX_RETURNS      = 3
    MAX_COMPLEXITY   = 5

    def __init__(self, llm):
        super().__init__(llm, name="LongFunctionAgent")

    # ──────────────────────────────────────────
    # Détection AST
    # ──────────────────────────────────────────

    def analyze(self, code: str, language: str = "python") -> List[str]:
        """
        Détecte via AST :
        - Fonctions trop longues (lignes)
        - Fonctions avec trop d'instructions
        - Fonctions avec trop de paramètres
        - Fonctions avec trop de points de retour
        - Fonctions avec complexité cyclomatique élevée
        - Fonctions imbriquées (candidates à l'extraction)
        Retourne toujours au moins un élément.
        """
        issues = []
        lang = language.lower()

        if lang == "python":
            issues += self._analyze_python(code)
        elif lang in ("javascript", "typescript"):
            issues += self._analyze_js(code)
        else:
            issues.append(
                f"Analyse des fonctions longues {language} — découpage via LLM"
            )

        if not issues:
            issues.append(
                "Analyse préventive — vérification de la longueur et cohérence des fonctions"
            )

        return issues

    def _analyze_python(self, code: str) -> List[str]:
        issues = []

        try:
            tree = ast.parse(code)
        except SyntaxError as e:
            return [f"Erreur de syntaxe — analyse impossible : {e}"]

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue

            name = node.name
            start = node.lineno
            end   = getattr(node, "end_lineno", start)
            length = end - start

            # 1) Trop longue en lignes
            if length > self.MAX_LINES:
                issues.append(
                    f"Fonction '{name}' trop longue : {length} lignes "
                    f"(seuil {self.MAX_LINES}) — ligne {start}"
                )

            # 2) Trop d'instructions directes
            stmt_count = len(node.body)
            if stmt_count > self.MAX_STATEMENTS:
                issues.append(
                    f"Fonction '{name}' : {stmt_count} instructions directes "
                    f"(seuil {self.MAX_STATEMENTS}) — ligne {start}"
                )

            # 3) Trop de paramètres
            params = (
                node.args.args
                + node.args.posonlyargs
                + node.args.kwonlyargs
            )
            if len(params) > self.MAX_PARAMS:
                issues.append(
                    f"Fonction '{name}' : {len(params)} paramètres "
                    f"(seuil {self.MAX_PARAMS}) — ligne {start}"
                )

            # 4) Trop de points de retour
            returns = sum(
                1 for n in ast.walk(node)
                if isinstance(n, ast.Return)
            )
            if returns > self.MAX_RETURNS:
                issues.append(
                    f"Fonction '{name}' : {returns} points de retour "
                    f"(seuil {self.MAX_RETURNS}) — ligne {start}"
                )

            # 5) Complexité cyclomatique élevée
            cc = self._cyclomatic_complexity(node)
            if cc > self.MAX_COMPLEXITY:
                issues.append(
                    f"Fonction '{name}' : complexité cyclomatique {cc} "
                    f"(seuil {self.MAX_COMPLEXITY}) — ligne {start}"
                )

            # 6) Fonctions imbriquées (candidates à l'extraction)
            nested = [
                n.name for n in ast.walk(node)
                if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                and n is not node
            ]
            if nested:
                issues.append(
                    f"Fonction '{name}' contient des fonctions imbriquées : "
                    f"{', '.join(nested)} — candidates à l'extraction"
                )

            # 7) Responsabilités mixtes (heuristique : mélange I/O + calcul + UI)
            mixed = self._detect_mixed_responsibilities(node)
            if mixed:
                issues.append(
                    f"Fonction '{name}' : responsabilités mixtes détectées "
                    f"({', '.join(mixed)})"
                )

        return issues

    def _cyclomatic_complexity(self, func_node) -> int:
        count = 1
        for node in ast.walk(func_node):
            if isinstance(node, (ast.If, ast.For, ast.While,
                                  ast.ExceptHandler, ast.With,
                                  ast.Assert, ast.comprehension)):
                count += 1
            elif isinstance(node, ast.BoolOp):
                count += len(node.values) - 1
        return count

    def _detect_mixed_responsibilities(self, func_node) -> List[str]:
        """Détecte heuristiquement les responsabilités mixtes."""
        responsibilities = []

        calls = [
            node.func.attr if isinstance(node.func, ast.Attribute) else
            (node.func.id if isinstance(node.func, ast.Name) else "")
            for node in ast.walk(func_node)
            if isinstance(node, ast.Call)
        ]
        calls_str = " ".join(calls).lower()

        io_keywords      = {"print", "write", "read", "open", "close", "input"}
        db_keywords      = {"execute", "query", "commit", "fetchall", "fetchone"}
        http_keywords    = {"get", "post", "put", "delete", "request", "fetch"}
        compute_keywords = {"sort", "filter", "map", "reduce", "sum", "max", "min"}

        found_groups = []
        if any(k in calls_str for k in io_keywords):
            found_groups.append("I/O")
        if any(k in calls_str for k in db_keywords):
            found_groups.append("base de données")
        if any(k in calls_str for k in http_keywords):
            found_groups.append("HTTP")
        if any(k in calls_str for k in compute_keywords):
            found_groups.append("calcul")

        if len(found_groups) >= 2:
            responsibilities = found_groups

        return responsibilities

    def _analyze_js(self, code: str) -> List[str]:
        """Analyse textuelle pour JS/TS."""
        issues = []
        lines  = code.splitlines()

        func_pattern = re.compile(
            r"(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s*)?\(|(\w+)\s*\(.*\)\s*\{)"
        )

        i = 0
        while i < len(lines):
            match = func_pattern.search(lines[i])
            if match:
                func_name = next(g for g in match.groups() if g) if any(match.groups()) else "anonymous"
                brace_count = 0
                start = i
                for j in range(i, len(lines)):
                    brace_count += lines[j].count("{") - lines[j].count("}")
                    if brace_count <= 0 and j > start:
                        length = j - start
                        if length > self.MAX_LINES:
                            issues.append(
                                f"Fonction JS '{func_name}' trop longue : "
                                f"{length} lignes (seuil {self.MAX_LINES}) — ligne {start + 1}"
                            )
                        i = j
                        break
            i += 1

        if not issues:
            issues.append("Fonctions JS/TS analysées — longueur acceptable")

        return issues

    # ──────────────────────────────────────────
    # Prompt
    # ──────────────────────────────────────────

    def build_prompt(self, code: str, language: str) -> str:
        return f"""You are an expert code refactoring agent specialized in decomposing long functions in {language}.

### Long function smells to fix
- Functions exceeding {self.MAX_LINES} lines
- Functions with more than {self.MAX_STATEMENTS} direct statements
- Functions with more than {self.MAX_PARAMS} parameters (introduce parameter objects)
- Functions with more than {self.MAX_RETURNS} return points
- Functions with cyclomatic complexity above {self.MAX_COMPLEXITY}
- Nested functions that can be extracted to the module level
- Functions mixing multiple responsibilities (I/O + computation + UI)

### Decomposition strategies
- Extract cohesive blocks into well-named helper functions
- One function = one responsibility (Single Responsibility Principle)
- Name extracted functions by WHAT they do, not HOW
- Use parameter objects (dataclass or dict) to reduce parameter count
- Extract guard clauses to reduce nesting and return points
- Separate data transformation from I/O operations
- Keep the public API function as a coordinator that calls helpers

### Strict constraints
- Preserve EXACT behavior for all inputs and edge cases
- Do not change return values, side effects, raised exceptions, or execution order
- Do not change public APIs or the original function signature
- Preserve logging, I/O, randomness, and global state
- Only extract when the extracted block has clear cohesion

### Output format
Return ONLY the refactored {language} code.
No explanation, no markdown, no comments.
First line must be code ({language} import, def, or class).
"""

    # ──────────────────────────────────────────
    # Apply avec RAG
    # ──────────────────────────────────────────

    def apply(
        self,
        code: str,
        language: str,
        temperature: Optional[float] = None,
        rag_context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:

        analysis      = self.analyze(code, language)
        system_prompt = self.build_prompt(code, language)

        # ⭐ _call_llm injecte rag_context automatiquement
        proposal = self._call_llm(
            system_prompt=system_prompt,
            user_prompt=code,
            temperature=temperature,
            rag_context=rag_context,
        )

        if not proposal or proposal.strip() == code.strip():
            proposal = code

        return {
            "name":             self.name,
            "analysis":         analysis,
            "proposal":         proposal,
            "temperature_used": temperature,
        }