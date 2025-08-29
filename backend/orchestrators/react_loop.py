from __future__ import annotations
from datetime import datetime, timedelta
from typing import Any, Dict, List

from utils.types import TripRequest, DayPlan, Plan
from utils.trace import DecisionTrace
from agents.planner import PlannerAgent
from agents.critic import CriticAgent
from agents.budget import BudgetAgent


class ReactLoop:
    """
    Minimal ReAct-style coordination:
      Planner -> Critic -> Budget -> Compose final Plan
    All agents share a single DecisionTrace for explainability.
    """

    def __init__(self) -> None:
        self.trace = DecisionTrace()
        self.planner = PlannerAgent(self.trace)
        self.critic = CriticAgent(self.trace)
        self.budget = BudgetAgent(self.trace)

    def run(self, request: TripRequest) -> Plan:
        state: Dict[str, Any] = {"request": request}

        # 1) Planner drafts a plan
        state.update(self.planner.act(state))

        # 2) Critic reviews and flags issues/suggestions
        state.update(self.critic.act(state))

        # 3) Budget estimates total cost
        state.update(self.budget.act(state))

        # 4) Compose final Plan object
        start = datetime.fromisoformat(request.start_date)  # expects YYYY-MM-DD
        day_plans: List[DayPlan] = []
        for d in state.get("draft_plan", []):
            date_str = (start + timedelta(days=int(d["day"]) - 1)).date().isoformat()
            day_plans.append(
                DayPlan(day=int(d["day"]), date=date_str, activities=list(d.get("activities", [])))
            )

        metadata = {
            "critic_issues": state.get("critic_issues", []),
            "critic_suggestions": state.get("critic_suggestions", []),
            "activity_pool": state.get("activity_pool", []),
        }

        total = float(state.get("total_cost_estimate", 0.0))
        return Plan(
            destination=request.destination,
            total_estimated_cost=total,
            days=day_plans,
            trace=self.trace.dump(),
            metadata=metadata,
        )
