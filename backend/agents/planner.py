from __future__ import annotations
from typing import Any, Dict, List
from .base import Agent
from utils.types import TripRequest

GENERIC_ACTIVITIES = [
    "City walking tour",
    "Top local museum",
    "Iconic viewpoint",
    "Historic district",
    "Local food market",
    "Park or waterfront",
]

class PlannerAgent(Agent):
    name = "Planner"

    def _build_pool(self, req: TripRequest, candidate_activities: List[str] | None) -> List[str]:
        # Start with explicit candidates if provided, else generic
        pool = list(candidate_activities) if candidate_activities else list(GENERIC_ACTIVITIES)

        # Light personalization: bias the pool with interests at the front
        # (keeps it deterministic for now; LLM-based expansion comes later)
        for interest in (req.profile.interests or [])[:3]:
            pool.insert(0, f"Explore {interest} scene")

        # De-duplicate while preserving order
        seen = set()
        unique_pool: List[str] = []
        for item in pool:
            if item not in seen:
                unique_pool.append(item)
                seen.add(item)
        return unique_pool

    def act(self, state: Dict[str, Any]) -> Dict[str, Any]:
        req: TripRequest = state["request"]
        pool = self._build_pool(req, state.get("candidate_activities"))

        self.log(f"planning {req.days} day(s) for {req.destination}; interests={req.profile.interests or 'none'}")
        draft_plan: List[Dict[str, Any]] = []

        # Simple deterministic schedule: 3 activities/day, round-robin from pool
        for d in range(req.days):
            activities = [pool[(d * 3 + i) % len(pool)] for i in range(3)]
            draft_plan.append({"day": d + 1, "activities": activities})

        return {"draft_plan": draft_plan, "activity_pool": pool}
