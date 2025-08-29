from __future__ import annotations
from typing import Any, Dict
from .base import Agent
from ..utils.types import TripRequest

DEFAULT_DAILY_COST_PER_PERSON = 120.0  # USD, conservative baseline

class BudgetAgent(Agent):
    name = "Budget"

    def act(self, state: Dict[str, Any]) -> Dict[str, Any]:
        req: TripRequest = state["request"]
        people = max(req.profile.people, 1)
        baseline = DEFAULT_DAILY_COST_PER_PERSON * req.days * people

        # If user provided a target total budget, keep both numbers
        target_budget = req.profile.budget_total
        result = {
            "total_cost_estimate": round(baseline, 2),
            "budget_target": target_budget,
        }

        if target_budget is not None and baseline > float(target_budget):
            self.log(
                f"estimate ${baseline:.2f} exceeds target ${float(target_budget):.2f} "
                f"by ${baseline - float(target_budget):.2f}"
            )
        else:
            self.log(f"estimated total ${baseline:.2f} for {people} traveler(s)")

        return result
