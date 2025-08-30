from __future__ import annotations
from typing import List, Dict, Any, Sequence

from agents.base import BaseAgent  # already in your repo
from utils.llm import ranked_spots_via_llm, flatten_spots_to_activity_strings


class DestinationLLMAgent(BaseAgent):
    """
    Uses an LLM to curate destination-specific 'best places' aligned to interests,
    then flattens them into concise activity strings that our Planner can consume.
    """

    name = "destination_llm"

    def propose(self, destination: str, interests: Sequence[str] | None, days: int) -> Dict[str, Any]:
        # Ask the LLM for top spots (rich objects)
        spots = ranked_spots_via_llm(destination=destination, interests=interests, days=days)

        # Flatten to short activity strings (for the current Plan schema)
        activities: List[str] = flatten_spots_to_activity_strings(spots)

        # Build trace lines
        trace_lines: List[str] = []
        if spots:
            trace_lines.append(
                f"[LLM] curated {len(spots)} high-signal spots for {destination}"
                + (f" (interests: {', '.join(interests)})" if interests else "")
            )
            # show a couple of examples for transparency
            preview = ", ".join([s.get("title", "") for s in spots[:3] if s.get("title")]) or "n/a"
            trace_lines.append(f"[LLM] examples: {preview}")
        else:
            trace_lines.append("[LLM] no LLM spots available (provider off or parsing failed)")

        return {
            "spots": spots,            # rich objects (for metadata / UI)
            "activities": activities,  # short strings (for Planner seeding)
            "trace": trace_lines,
        }
