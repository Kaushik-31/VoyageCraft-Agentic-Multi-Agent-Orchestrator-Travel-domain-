from __future__ import annotations
from typing import Any, Dict, List
from .base import Agent

class CriticAgent(Agent):
    name = "Critic"

    def act(self, state: Dict[str, Any]) -> Dict[str, Any]:
        draft: List[Dict[str, Any]] = state.get("draft_plan", [])
        issues: List[str] = []
        suggestions: List[str] = []

        # 1) Per-day duplicate check
        for day in draft:
            acts = day.get("activities", [])
            if len(set(acts)) < len(acts):
                issues.append(f"Day {day['day']}: duplicated activities")
                suggestions.append(f"Day {day['day']}: replace duplicates with alternatives from pool")

        # 2) Repetition across consecutive days (fatigue heuristic)
        prev = set()
        for day in draft:
            acts = set(day.get("activities", []))
            if prev and len(prev.intersection(acts)) >= 2:
                issues.append(f"Day {day['day']}: heavy overlap with previous day")
                suggestions.append(f"Day {day['day']}: swap 1–2 items for variety")
            prev = acts

        if issues:
            self.log(f"found {len(issues)} issue(s)")
        else:
            self.log("no obvious issues found")

        return {"critic_issues": issues, "critic_suggestions": suggestions}
