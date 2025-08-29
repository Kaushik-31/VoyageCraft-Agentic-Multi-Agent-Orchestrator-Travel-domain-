from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Any, Dict
from ..utils.trace import DecisionTrace

class Agent(ABC):
    """
    Minimal base class for all agents.
    Each agent receives a shared DecisionTrace for explainability.
    """

    name: str = "Agent"

    def __init__(self, trace: DecisionTrace) -> None:
        self.trace = trace

    def log(self, message: str) -> None:
        self.trace.log(f"[{self.name}] {message}")

    @abstractmethod
    def act(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Read 'state' (a shared dict), optionally add keys, and return a partial update dict.
        Orchestrators merge these updates back into the state.
        """
        raise NotImplementedError
