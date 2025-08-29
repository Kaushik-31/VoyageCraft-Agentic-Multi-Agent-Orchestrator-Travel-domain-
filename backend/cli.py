from __future__ import annotations

import json
import typer
from rich.console import Console

from orchestrators.react_loop import ReactLoop
from utils.types import TripRequest, UserProfile

console = Console()

def main(
    origin: str = typer.Option("Chicago", help="Starting city or airport"),
    destination: str = typer.Option("Paris", help="Destination city"),
    start_date: str = typer.Option("2025-09-10", help="YYYY-MM-DD"),
    days: int = typer.Option(3, min=1, max=30, help="Trip length in days"),
    people: int = typer.Option(2, min=1, help="Number of travelers"),
    budget_total: float = typer.Option(1000.0, min=0.0, help="Total budget in USD"),
    interests: str = typer.Option("art,cafes", help="Comma-separated interests"),
):
    """
    Run the ReAct-style loop (Planner -> Critic -> Budget) and print a JSON plan + decision trace.
    """
    interests_list = [s.strip() for s in interests.split(",") if s.strip()]
    profile = UserProfile(people=people, budget_total=budget_total, interests=interests_list)
    req = TripRequest(
        origin=origin,
        destination=destination,
        start_date=start_date,
        days=days,
        profile=profile,
    )

    orch = ReactLoop()
    plan = orch.run(req)

    console.rule("[bold]VoyageCraft Simulation[/bold]")
    console.print_json(json.dumps(plan.model_dump(), indent=2))
    console.rule()

if __name__ == "__main__":
    typer.run(main)
