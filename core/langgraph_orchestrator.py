"""
Orchestrateur LangGraph avec intégration GraphRAG.
"""

from typing import Dict, List, Any, Optional
import time

from agents.rename_agent import RenameAgent
from agents.complexity_agent import ComplexityAgent
from agents.duplication_agent import DuplicationAgent
from agents.import_agent import ImportAgent
from agents.long_function_agent import LongFunctionAgent
from agents.merge_agent import MergeAgent
from agents.test_agent import TestAgent
from agents.patch_agent import PatchAgent
from core.temperature_config import TemperatureConfig

from .workflow_state import RefactorState
from .workflow_graph import compile_graph

# ⭐ Import RAG — non bloquant si absent
try:
    from graphrag.graphrag_retriever import GraphRAGRetriever
    _RAG_AVAILABLE = True
except ImportError:
    _RAG_AVAILABLE = False


class LangGraphOrchestrator:
    """
    Orchestrateur intelligent basé sur LangGraph.
    Supporte les températures personnalisées et le contexte GraphRAG.
    """

    def __init__(self, llm):
        self.agent_instances = {
            "RenameAgent":        RenameAgent(llm),
            "ComplexityAgent":    ComplexityAgent(llm),
            "DuplicationAgent":   DuplicationAgent(llm),
            "ImportAgent":        ImportAgent(llm),
            "LongFunctionAgent":  LongFunctionAgent(llm),
            "TestAgent":          TestAgent(llm),
            "PatchAgent":         PatchAgent(llm),
        }
        self.merge_agent = MergeAgent(llm)
        self.temperature_config = TemperatureConfig()

        # ⭐ Initialiser le retriever RAG une seule fois
        self.rag_retriever: Optional[Any] = None
        if _RAG_AVAILABLE:
            try:
                self.rag_retriever = GraphRAGRetriever()
                print("✅ GraphRAG retriever chargé")
            except Exception as e:
                print(f"⚠️  GraphRAG non disponible : {e}")

        self.graph = compile_graph(self)

    # ──────────────────────────────────────────
    # RAG
    # ──────────────────────────────────────────

    def _retrieve_rag_context(
        self,
        language: str,
        selected_agents: List[str],
    ) -> Optional[Dict[str, Any]]:
        """
        Interroge le GraphRAG et retourne un dict de contexte.
        Retourne None si le RAG n'est pas disponible ou échoue.
        """
        if not self.rag_retriever:
            return None

        try:
            query = (
                f"refactoring best practices {language} "
                + " ".join(selected_agents)
            )
            pack = self.rag_retriever.retrieve(query)

            context_str = GraphRAGRetriever.format_context(pack)
            symbols = pack.get("symbols", [])
            sources = [s["source"] for s in pack.get("seeds", [])]
            chunks_count = len(pack.get("chunks", []))

            print(f"   📚 RAG : {chunks_count} chunks — {len(symbols)} symboles")

            return {
                "context_str": context_str,
                "symbols":     symbols,
                "sources":     sources,
            }

        except Exception as e:
            print(f"⚠️  RAG retrieve échoué : {e}")
            return None

    # ──────────────────────────────────────────
    # Workflow principal
    # ──────────────────────────────────────────

    def run_workflow(
        self,
        code: str,
        language: str,
        selected_agents: Optional[List[str]] = None,
        auto_patch: bool = True,
        auto_test: bool = True,
        temperature_override: Optional[Dict[str, float]] = None,
        use_rag: bool = True,
    ) -> Dict[str, Any]:
        """
        Exécute le workflow complet de refactoring.

        Args:
            code:                Code source à refactorer.
            language:            Langage de programmation.
            selected_agents:     Agents à exécuter (tous si None).
            auto_patch:          Activer la boucle PatchAgent.
            auto_test:           Activer TestAgent dans la boucle.
            temperature_override: Températures LLM par agent.
            use_rag:             Activer le contexte GraphRAG (défaut True).

        Returns:
            Dict complet avec code refactoré, résultats agents et métriques.
        """
        if selected_agents is None:
            selected_agents = self.get_refactoring_agents()

        if temperature_override is None:
            temperature_override = {}

        print(f"🚀 Démarrage du workflow LangGraph avec {len(selected_agents)} agents")
        if temperature_override:
            print(f"   🌡️  Températures personnalisées: {temperature_override}")

        # ⭐ Récupérer le contexte RAG avant de lancer le graphe
        rag_context = None
        if use_rag:
            rag_context = self._retrieve_rag_context(language, selected_agents)
            if rag_context:
                print(f"   📖 Contexte RAG prêt ({len(rag_context['sources'])} sources)")
            else:
                print("   ℹ️  Aucun contexte RAG — fonctionnement sans RAG")

        workflow_start_time = time.time()

        initial_state: RefactorState = {
            "_orchestrator":        self,
            "original_code":        code,
            "language":             language,
            "current_code":         code,
            "current_agent":        None,
            "agent_results":        [],
            "issues_detected":      [],
            "history":              [],
            "selected_agents":      selected_agents,
            "temperature_config":   self.temperature_config,
            "temperature_override": temperature_override,
            "auto_patch":           auto_patch,
            "auto_test":            auto_test,
            "patch_test_iteration": 0,
            "patch_test_errors":    [],
            "patch_test_status":    "pending",
            "rag_context":          rag_context,  # ⭐ RAG
            "metrics":              {},
            "error":                None,
            "status":               "initialized",
            "patch_result":         None,
            "test_result":          None,
            "final_code":           None,
        }

        try:
            final_state = self.graph.invoke(initial_state)

            workflow_duration = time.time() - workflow_start_time
            final_state["final_code"] = final_state.get("current_code", code)
            final_state["metrics"]["workflow_duration"] = workflow_duration

            return self._prepare_final_report(final_state)

        except Exception as e:
            print(f"❌ Erreur dans le workflow : {e}")
            import traceback
            traceback.print_exc()

            return {
                "success":        False,
                "error":          str(e),
                "refactored_code": code,
                "final_code":     code,
                "agent_results":  [],
            }

    # ──────────────────────────────────────────
    # Rapport
    # ──────────────────────────────────────────

    def _prepare_final_report(self, final_state: RefactorState) -> Dict[str, Any]:
        agent_results = []

        for ar in final_state.get("agent_results", []):
            agent_results.append({
                "name":             ar.name,
                "analysis":         ar.analysis,
                "temperature_used": ar.temperature_used,
                "duration":         ar.duration,
                "status":           ar.status,
            })

        patch_result = final_state.get("patch_result")
        if patch_result:
            agent_results.append({
                "name":             "PatchAgent",
                "analysis":         patch_result.get("analysis", []),
                "temperature_used": None,
                "duration":         patch_result.get("duration", 0),
                "status":           patch_result.get("status", "SUCCESS"),
            })

        test_result = final_state.get("test_result")
        if test_result:
            agent_results.append({
                "name":             "TestAgent",
                "analysis":         [],
                "temperature_used": None,
                "duration":         test_result.get("duration", 0),
                "status":           test_result.get("status", "UNKNOWN"),
            })

        rag_ctx = final_state.get("rag_context")
        rag_info = None
        if rag_ctx:
            rag_info = {
                "sources":      rag_ctx.get("sources", []),
                "symbols_used": rag_ctx.get("symbols", [])[:20],
            }

        return {
            "success":         True,
            "refactored_code": final_state.get("final_code", final_state["original_code"]),
            "original_code":   final_state["original_code"],
            "language":        final_state["language"],
            "agent_results":   agent_results,
            "issues_detected": final_state.get("issues_detected", []),
            "history":         final_state.get("history", []),
            "metrics":         final_state.get("metrics", {}),
            "patch_result":    patch_result,
            "test_result":     test_result,
            "rag_info":        rag_info,  # ⭐ RAG info dans le rapport
            "execution_time":  final_state.get("metrics", {}).get("workflow_duration", 0),
        }

    # ──────────────────────────────────────────
    # Compatibilité ancienne API
    # ──────────────────────────────────────────

    def run_parallel(self, code, selected_agent_names, language, temperature_override=None):
        result = self.run_workflow(
            code=code,
            language=language,
            selected_agents=selected_agent_names,
            auto_patch=False,
            auto_test=False,
            temperature_override=temperature_override,
        )
        return [
            {
                "name":             r["name"],
                "analysis":         r["analysis"],
                "proposal":         result["refactored_code"],
                "temperature_used": r.get("temperature_used"),
                "duration":         r.get("duration", 0),
            }
            for r in result.get("agent_results", [])
        ]

    def merge_results(self, original_code, selected_results):
        if not selected_results:
            return original_code
        proposals = [
            r.get("proposal", "")
            for r in selected_results
            if r.get("proposal") and r.get("proposal") != original_code
        ]
        return self.merge_agent.merge(original_code, proposals, temperature=0.2)

    def run_patch_and_test(self, code, language, patch=True, test=True):
        patch_result = None
        test_result  = None
        if patch:
            pa = self.agent_instances.get("PatchAgent")
            if pa:
                patch_result = pa.apply(code, language=language)
                code = patch_result["proposal"]
        if test:
            ta = self.agent_instances.get("TestAgent")
            if ta:
                test_result = ta.apply(code, language=language)
        return code, patch_result, test_result

    def get_available_agents(self):
        return list(self.agent_instances.keys())

    def get_refactoring_agents(self):
        return [
            name for name in self.agent_instances
            if name not in ("TestAgent", "PatchAgent", "MergeAgent")
        ]


Orchestrator = LangGraphOrchestrator