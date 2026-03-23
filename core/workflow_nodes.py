"""
Nœuds pour le workflow LangGraph de refactoring.
Chaque nœud est une fonction qui prend l'état en entrée et le modifie.
"""

from typing import Dict, Any
from .workflow_state import RefactorState
import time

def initialize_node(state: RefactorState) -> RefactorState:
    """Nœud d'initialisation : prépare l'état"""
    print(f"🔧 Initialisation du workflow pour {state['language']}")
    
    state["current_code"] = state["original_code"]
    state["agent_results"] = []
    state["issues_detected"] = []
    state["history"] = []
    state["status"] = "analyzing"
    state["metrics"] = {
        "start_time": time.time(),
        "agents_executed": 0,
        "issues_found": 0,
        "code_length_original": len(state["original_code"])
    }
    
    # Enregistrer dans l'historique
    state["history"].append({
        "timestamp": time.time(),
        "action": "initialize",
        "message": f"Workflow démarré avec {len(state['selected_agents'])} agents sélectionnés"
    })
    
    return state

def analyze_issues_node(state: RefactorState) -> RefactorState:
    """Nœud d'analyse : détecte les problèmes dans le code"""
    print("🔍 Analyse des problèmes...")
    
    # Ici, on pourrait ajouter une analyse heuristique pour décider
    # quels agents exécuter en priorité, mais pour maintenant,
    # on exécutera simplement tous les agents sélectionnés
    
    state["history"].append({
        "timestamp": time.time(),
        "action": "analyze",
        "message": f"Analyse terminée - {len(state['selected_agents'])} agents à exécuter"
    })
    
    return state

def execute_refactoring_agent_node(state: RefactorState, agent_name: str) -> RefactorState:
    """Nœud d'exécution d'un agent de refactoring spécifique"""
    print(f"⚡ Exécution de {agent_name}...")
    
    # Cette fonction serait appelée pour chaque agent
    # Dans l'implémentation finale, on utiliserait les agents existants
    
    state["current_agent"] = agent_name
    state["history"].append({
        "timestamp": time.time(),
        "action": "execute_agent",
        "agent": agent_name
    })
    
    return state

def decide_next_agent_node(state: RefactorState) -> Dict[str, Any]:
    """
    Nœud de décision : choisit le prochain agent à exécuter.
    Retourne le nom du prochain nœud à exécuter.
    """
    # Logique de décision intelligente
    executed_agents = [r.name for r in state.get("agent_results", [])]
    remaining_agents = [
        agent for agent in state["selected_agents"] 
        if agent not in executed_agents 
        and agent not in ["TestAgent", "PatchAgent", "MergeAgent"]
    ]
    
    if remaining_agents:
        # Exécuter le prochain agent
        next_agent = remaining_agents[0]
        return {"next": "execute_refactoring_agent", "agent": next_agent}
    
    # Tous les agents de refactoring sont terminés
    return {"next": "merge_results"}

def merge_results_node(state: RefactorState) -> RefactorState:
    """Nœud de fusion des résultats des agents"""
    print("🔄 Fusion des résultats...")
    
    # Pour l'instant, on garde le code tel quel
    # Dans l'implémentation finale, on utiliserait le MergeAgent
    
    state["history"].append({
        "timestamp": time.time(),
        "action": "merge",
        "message": "Fusion des propositions d'agents"
    })
    
    state["status"] = "patching"
    return state

def apply_patch_node(state: RefactorState) -> RefactorState:
    """Nœud d'application du PatchAgent"""
    if not state.get("auto_patch", True):
        print("⏭️ PatchAgent désactivé")
        return state
    
    print("🩹 Application du PatchAgent...")
    
    state["history"].append({
        "timestamp": time.time(),
        "action": "patch",
        "message": "PatchAgent appliqué"
    })
    
    state["status"] = "testing"
    return state

def run_tests_node(state: RefactorState) -> RefactorState:
    """Nœud d'exécution du TestAgent"""
    if not state.get("auto_test", True):
        print("⏭️ TestAgent désactivé")
        return state
    
    print("🧪 Exécution du TestAgent...")
    
    state["history"].append({
        "timestamp": time.time(),
        "action": "test",
        "message": "TestAgent exécuté"
    })
    
    state["status"] = "completed"
    return state

def finalize_node(state: RefactorState) -> RefactorState:
    """Nœud de finalisation : calcule les métriques finales"""
    print("✅ Finalisation du workflow...")
    
    # Calculer les métriques finales
    execution_time = time.time() - state["metrics"]["start_time"]
    state["metrics"]["execution_time"] = execution_time
    state["metrics"]["agents_executed"] = len(state.get("agent_results", []))
    state["metrics"]["code_length_final"] = len(state.get("current_code", ""))
    
    # Définir le code final
    state["final_code"] = state.get("current_code", state["original_code"])
    
    state["history"].append({
        "timestamp": time.time(),
        "action": "finalize",
        "message": f"Workflow terminé en {execution_time:.2f}s"
    })
    
    return state

def handle_error_node(state: RefactorState, error: Exception) -> RefactorState:
    """Nœud de gestion d'erreur"""
    print(f"❌ Erreur dans le workflow : {error}")
    
    state["error"] = str(error)
    state["status"] = "failed"
    
    state["history"].append({
        "timestamp": time.time(),
        "action": "error",
        "message": str(error)
    })
    
    return state