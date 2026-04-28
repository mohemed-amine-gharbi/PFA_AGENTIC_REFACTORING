from typing import TypedDict, List, Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class AgentResult:
    name: str
    analysis: List[str]
    proposal: str
    temperature_used: Optional[float]
    duration: float
    status: str


class RefactorState(TypedDict):
    original_code: str
    language: str
    current_code: str

    current_agent: Optional[str]

    agent_results: List[AgentResult]
    issues_detected: List[str]

    history: List[str]
    selected_agents: List[str]
    temperature_config: Any
    temperature_override: Dict[str, float]

    auto_patch: bool
    auto_test: bool

    patch_test_iteration: int
    patch_test_errors: List[str]
    patch_test_status: str

    _orchestrator: Any

    # ⭐ RAG
    rag_context: Optional[Dict[str, Any]]

    metrics: Dict[str, Any]

    error: Optional[str]
    status: str
    patch_result: Optional[Dict[str, Any]]
    test_result: Optional[Dict[str, Any]]
    final_code: Optional[str]