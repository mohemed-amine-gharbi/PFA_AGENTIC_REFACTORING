"""
Graphe LangGraph pour le workflow de refactoring.
Passe rag_context à chaque agent via agent.apply().
"""

from typing import Dict, Any
import time
from langgraph.graph import StateGraph, END
from .workflow_state import RefactorState, AgentResult

MAX_PATCH_TEST_ITERATIONS = 3


# ──────────────────────────────────────────────────────────────
# Nœuds agents de refactoring
# ──────────────────────────────────────────────────────────────

def create_agent_node(orchestrator, agent_name: str):
    """
    Crée un nœud pour un agent de refactoring.
    Transmet temperature et rag_context à agent.apply().
    """
    def agent_node(state: RefactorState) -> RefactorState:
        print(f"\n🤖 Exécution de {agent_name}...")

        agent = orchestrator.agent_instances.get(agent_name)
        if not agent:
            print(f"⚠️  Agent {agent_name} non trouvé")
            return state

        current_code = state["current_code"]
        language     = state["language"]

        # Température
        temperature_override = state.get("temperature_override", {})
        if agent_name in temperature_override:
            temperature = temperature_override[agent_name]
            print(f"   🌡️  Température personnalisée : {temperature}")
        else:
            temperature = state["temperature_config"].get_temperature(agent_name)
            print(f"   🌡️  Température par défaut : {temperature}")

        # ⭐ Contexte RAG depuis l'état
        rag_context = state.get("rag_context")
        if rag_context:
            print(f"   📚 RAG actif ({len(rag_context.get('symbols', []))} symboles)")

        start_time = time.time()
        try:
            # ⭐ Passer rag_context à l'agent
            result = agent.apply(
                current_code,
                language,
                temperature=temperature,
                rag_context=rag_context,
            )
            duration = time.time() - start_time

            agent_result = AgentResult(
                name=agent_name,
                analysis=result.get("analysis", []),
                proposal=result.get("proposal", current_code),
                temperature_used=temperature,
                duration=duration,
                status="SUCCESS",
            )

            print(f"   ✅ Terminé en {duration:.2f}s")
            print(f"   📋 {len(agent_result.analysis)} problèmes détectés")

            new_state = state.copy()
            new_state["agent_results"]   = state["agent_results"] + [agent_result]
            new_state["current_agent"]   = agent_name
            new_state["current_code"]    = agent_result.proposal
            new_state["issues_detected"] = state["issues_detected"] + list(agent_result.analysis)
            new_state["history"]         = state["history"] + [f"{agent_name} executed"]
            return new_state

        except Exception as e:
            print(f"   ❌ Erreur : {e}")
            duration = time.time() - start_time
            agent_result = AgentResult(
                name=agent_name,
                analysis=[],
                proposal=current_code,
                temperature_used=temperature,
                duration=duration,
                status=f"FAILED: {str(e)[:100]}",
            )
            new_state = state.copy()
            new_state["agent_results"] = state["agent_results"] + [agent_result]
            new_state["history"]       = state["history"] + [f"{agent_name} failed: {str(e)[:50]}"]
            return new_state

    return agent_node


# ──────────────────────────────────────────────────────────────
# Routage entre agents
# ──────────────────────────────────────────────────────────────

def route_to_next_agent(state: RefactorState) -> str:
    selected  = state["selected_agents"]
    executed  = {r.name for r in state["agent_results"]}
    for name in selected:
        if name not in executed:
            return name
    return "merge"


# ──────────────────────────────────────────────────────────────
# Merge
# ──────────────────────────────────────────────────────────────

def merge_node(state: RefactorState) -> RefactorState:
    print("\n🔄 Fusion des résultats...")
    new_state = state.copy()
    new_state["status"]  = "merged"
    new_state["history"] = state["history"] + ["Results merged"]
    print("   ✅ Fusion terminée")
    return new_state


# ──────────────────────────────────────────────────────────────
# Boucle Patch / Test
# ──────────────────────────────────────────────────────────────

def patch_node(state: RefactorState) -> RefactorState:
    """PatchAgent — nettoie le code et corrige les erreurs remontées par TestAgent."""
    iteration = state["patch_test_iteration"] + 1
    print(f"\n🩹 PatchAgent (itération {iteration}/{MAX_PATCH_TEST_ITERATIONS})...")

    patch_agent = state["_orchestrator"].agent_instances.get("PatchAgent")
    if not patch_agent:
        return state

    errors   = state.get("patch_test_errors", [])
    code     = state["current_code"]
    language = state["language"]

    start        = time.time()
    patch_result = patch_agent.apply(code, language, errors=errors)
    duration     = time.time() - start

    new_state = state.copy()
    new_state["current_code"]        = patch_result.get("proposal", code)
    new_state["patch_result"]        = {**patch_result, "duration": duration, "status": "SUCCESS"}
    new_state["patch_test_iteration"] = iteration
    new_state["history"]             = state["history"] + [f"PatchAgent iteration {iteration}"]

    print(f"   ✅ Patch terminé en {duration:.2f}s")
    return new_state


def test_node(state: RefactorState) -> RefactorState:
    """TestAgent — analyse le code propre et collecte les erreurs."""
    iteration = state["patch_test_iteration"]
    print(f"\n🧪 TestAgent (itération {iteration}/{MAX_PATCH_TEST_ITERATIONS})...")

    test_agent = state["_orchestrator"].agent_instances.get("TestAgent")
    if not test_agent:
        return state

    start       = time.time()
    test_result = test_agent.apply(state["current_code"], state["language"])
    duration    = time.time() - start

    errors      = _extract_errors(test_result)
    test_status = "passed" if not errors else "failed"

    new_state = state.copy()
    new_state["test_result"]        = {**test_result, "duration": duration}
    new_state["patch_test_errors"]  = errors
    new_state["patch_test_status"]  = test_status
    new_state["history"]            = state["history"] + [
        f"TestAgent: {test_status} ({len(errors)} erreurs)"
    ]

    icon = "✅" if test_status == "passed" else "❌"
    print(f"   {icon} Test {test_status} en {duration:.2f}s — {len(errors)} erreur(s)")
    return new_state


def route_patch_test(state: RefactorState) -> str:
    """Décide si on reboucle vers patch ou si on termine."""
    status    = state.get("patch_test_status", "pending")
    iteration = state.get("patch_test_iteration", 0)

    if status == "passed":
        print(f"\n✅ Boucle patch/test terminée — code valide après {iteration} itération(s)")
        return END

    if iteration >= MAX_PATCH_TEST_ITERATIONS:
        print(f"\n⚠️  Itérations max ({MAX_PATCH_TEST_ITERATIONS}) atteintes — sortie forcée")
        return END

    print(f"\n🔄 Erreurs détectées — nouvelle itération patch ({iteration + 1}/{MAX_PATCH_TEST_ITERATIONS})")
    return "patch"


def _extract_errors(test_result: dict) -> list:
    """Collecte les erreurs bloquantes ET warnings depuis le résultat TestAgent."""
    errors = []
    for detail in test_result.get("details", []):
        tool   = detail.get("tool", "")
        status = detail.get("status", "")
        output = detail.get("output", "")
        if status in ("FAILED", "WARNING") and output and not output.startswith("✅"):
            errors.append(f"[{tool}] {output[:300]}")
    return errors


# ──────────────────────────────────────────────────────────────
# Compilation du graphe
# ──────────────────────────────────────────────────────────────

def compile_graph(orchestrator) -> StateGraph:
    workflow = StateGraph(RefactorState)

    # Nœuds agents de refactoring
    for agent_name in orchestrator.get_refactoring_agents():
        workflow.add_node(agent_name, create_agent_node(orchestrator, agent_name))

    # Nœuds fixes
    workflow.add_node("merge", merge_node)
    workflow.add_node("patch", patch_node)
    workflow.add_node("test",  test_node)

    # Entrée conditionnelle
    workflow.set_conditional_entry_point(
        route_to_next_agent,
        {name: name for name in orchestrator.get_refactoring_agents()},
    )

    # Agents → merge (conditionnel)
    for agent_name in orchestrator.get_refactoring_agents():
        workflow.add_conditional_edges(
            agent_name,
            route_to_next_agent,
            {
                **{name: name for name in orchestrator.get_refactoring_agents()},
                "merge": "merge",
            },
        )

    # merge → patch → test → (patch | END)
    workflow.add_edge("merge", "patch")
    workflow.add_edge("patch", "test")
    workflow.add_conditional_edges(
        "test",
        route_patch_test,
        {"patch": "patch", END: END},
    )

    return workflow.compile()