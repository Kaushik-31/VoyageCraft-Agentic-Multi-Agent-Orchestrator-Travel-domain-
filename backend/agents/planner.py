from __future__ import annotations
from datetime import datetime, timedelta
from typing import List, Sequence, Optional, Dict, Any

from agents.base import BaseAgent
from utils.types import TripRequest, DayPlan


class Planner(BaseAgent):
    """
    Drafts a day-by-day itinerary.
    If LLM seeds are provided, they are slotted first; otherwise fall back to generic activities
    aligned to interests.
    """
    name = "planner"
    _PER_DAY = 3  # activities per day (simple, editable)

    def run(self, request: TripRequest, seed_activities: Optional[List[str]] = None) -> Dict[str, Any]:
        destination = request.destination
        days = int(request.days)
        interests: Sequence[str] = request.profile.interests or []

        seeds = list(seed_activities or [])
        generic_pool = self._build_generic_pool(interests, destination)

        out_days: List[DayPlan] = []
        start_dt = datetime.fromisoformat(request.start_date)

        idx = 0  # pointer into seeds
        for d in range(days):
            acts: List[str] = []
            for _ in range(self._PER_DAY):
                if idx < len(seeds):
                    acts.append(seeds[idx])
                    idx += 1
                else:
                    # deterministic but varied fallback
                    if generic_pool:
                        pick = generic_pool[(d * self._PER_DAY + _) % len(generic_pool)]
                        acts.append(pick)
                    else:
                        acts.append("City walking tour")

            out_days.append(
                DayPlan(
                    day=d + 1,
                    date=(start_dt + timedelta(days=d)).date().isoformat(),
                    activities=acts,
                    notes=None,
                )
            )

        trace_lines: List[str] = []
        if seeds:
            used = min(len(seeds), days * self._PER_DAY)
            trace_lines.append(f"[Planner] used {used} LLM-seeded activities")
        else:
            trace_lines.append("[Planner] no seeds; used generic activities from interests")

        return {"days": out_days, "trace": trace_lines}

    # ---------- helpers ----------

    def _build_generic_pool(self, interests: Sequence[str], destination: str) -> List[str]:
        # very lightweight pool; expand freely
        m = {
            "art": ["Explore art scene", "Top local museum", "Gallery hop"],
            "cafes": ["Explore cafes scene", "Coffee tasting", "Historic district cafe"],
            "history": ["Old town walk", "Iconic landmark", "Heritage site"],
            "food": ["Local food market", "Street food crawl", "Neighborhood food court"],
            "nature": ["Park or waterfront", "City viewpoint", "Botanical garden"],
        }
        pool: List[str] = []
        for tag in interests:
            pool += m.get(tag.lower(), [])
        if not pool:
            pool = ["City walking tour", "Iconic viewpoint", "Local market"]
        # dedupe, preserve order
        seen = set()
        deduped: List[str] = []
        for s in pool:
            if s not in seen:
                deduped.append(s)
                seen.add(s)
        return deduped
