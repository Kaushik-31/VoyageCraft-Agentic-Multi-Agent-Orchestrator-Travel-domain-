from __future__ import annotations
from typing import List

class DecisionTrace:
    """
    Minimal append-only trace used by agents and orchestrators to log decisions.
    Keep it lightweight and serializable to JSON for API responses.
    """
    def __init__(self) -> None:
        self._events: List[str] = []

    def log(self, message: str) -> None:
        # Keep one-liners; agents can include their name like: "[Planner] ..."
        self._events.append(message)

    def extend(self, messages: List[str]) -> None:
        self._events.extend(messages)

    def dump(self) -> List[str]:
        return list(self._events)  # return a copy to avoid external mutation

    def __len__(self) -> int:
        return len(self._events)
