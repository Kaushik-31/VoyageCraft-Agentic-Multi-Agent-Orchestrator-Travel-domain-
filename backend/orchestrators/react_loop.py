from __future__ import annotations
from typing import List, Dict, Any

from utils.types import TripRequest, Plan, DayPlan
from agents.planner import Planner
from agents.critic import Critic
from agents.budget import Budget
from agents.destination_llm import DestinationLLMAgent
from utils.config import get_settings, choose_llm


class ReactLoop:
    """
    Simple orchestrator:
      1) Ask LLM for destination-specific 'best places' (rich spots + seed activities)
      2) Planner drafts days (uses seeds first, then generic fallbacks)
      3) Critic sanity-checks
      4) Budget estimates total cost
      5) Return a Plan with decision trace + metadata (incl. llm_spots)
    """

    def run(self, request: TripRequest) -> Plan:
        trace: List[str] = []
        metadata: Dict[str, Any] = {}

        # -------- 1) LLM destination curation
        interests = request.profile.interests or []
        llm_agent = DestinationLLMAgent()
        llm_out = llm_agent.propose(
            destination=request.destination,
            interests=interests,
            days=request.days,
        )
        seed_activities = llm_out.get("activities", [])
        llm_spots = llm_out.get("spots", [])
        trace.extend(llm_out.get("trace", []))

        if llm_spots:
            # record provider/model for transparency
            s = get_settings()
            picked = choose_llm(s)
            if picked:
                provider, cfg = picked
                metadata["llm_provider"] = provider
                metadata["llm_model"] = cfg.get("model")
            metadata["llm_spots"] = llm_spots

        # -------- 2) Planning
        planner = Planner()
        pr = planner.run(request, seed_activities=seed_activities)
        days: List[DayPlan] = pr["days"]
        trace.extend(pr.get("trace", []))

        # -------- 3) Critic (structure-aware but lightweight)
        critic = Critic()
        critic_trace: List[str] = []
        if hasattr(critic, "run"):
            out = critic.run(days, request)  # type: ignore[arg-type]
            if isinstance(out, dict) and "trace" in out:
                critic_trace = out["trace"]
            elif isinstance(out, str):
                critic_trace = [out]
        elif hasattr(critic, "review"):
            msg = critic.review(days, request)  # type: ignore[attr-defined]
            critic_trace = [msg] if isinstance(msg, str) else (msg or [])
        if not critic_trace:
            critic_trace = ["[Critic] no obvious issues found"]
        trace.extend(critic_trace)

        # -------- 4) Budget
        # fall back to a deterministic simple estimate if the Budget agent shape differs
        total = None
        currency = "USD"
        budget = Budget()
        if hasattr(budget, "estimate"):
            bo = budget.estimate(days, request)  # type: ignore[attr-defined]
            if isinstance(bo, dict):
                total = int(bo.get("total_estimated_cost") or bo.get("total") or 0)
                currency = bo.get("currency", "USD")
                if "trace" in bo:
                    trace.extend(bo["trace"])
        if total is None:
            # default rule-of-thumb: $120 per person per day
            per_ppd = 120
            total = int(per_ppd * request.profile.people * request.days)
            trace.append(
                f"[Budget] estimated total ${total:.2f} for {request.profile.people} traveler(s)"
            )

        # -------- 5) Return Plan
        plan = Plan(
            destination=request.destination,
            total_estimated_cost=total,
            currency=currency,
            days=days,
            trace=trace,
            metadata=metadata,
        )
        return plan
