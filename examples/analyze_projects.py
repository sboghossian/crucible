"""
Example: Full research run on a codebase + naming debate.

Demonstrates:
1. Scanner agent analyzing a real repo
2. Research agent synthesizing knowledge
3. Pattern analyst finding cross-project patterns
4. Debate Council — the crown jewel — deciding EVERYTHING:
   - Project naming ("Crucible" vs alternatives)
   - Primary research focus
   - Architecture recommendation
5. Forecaster + Visualizer + Publisher pipeline

Usage:
    export ANTHROPIC_API_KEY=sk-...
    python examples/analyze_projects.py
    python examples/analyze_projects.py --repo /path/to/your/repo
    python examples/analyze_projects.py --debate-only  # just run the naming debate
"""

from __future__ import annotations

import argparse
import asyncio
import json
import logging
import os
import sys
from pathlib import Path

# Allow running from project root without installing
sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.table import Table

from crucible import Orchestrator
from crucible.debate import format_summary, resolve
from crucible.debate.protocol import DebateProtocol

console = Console()
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(name)s] %(message)s")


# ---------------------------------------------------------------------------
# 1. Project naming debate — the canonical Crucible example
# ---------------------------------------------------------------------------

async def debate_project_naming(api_key: str, model: str) -> None:
    """
    The Debate Council deliberates: what should this framework be named?
    "Crucible" vs 4 serious alternatives. Every decision goes through the council.
    """
    console.rule("[bold cyan]CRUCIBLE — Project Naming Debate[/bold cyan]")
    console.print(
        "\n[dim]The 4 personas will debate the name for this multi-agent research framework.[/dim]\n"
    )

    orch = Orchestrator(api_key=api_key, model=model)

    result = await orch.standalone_debate(
        topic="What should this multi-agent research framework be named?",
        context="""This is a Python framework that:
- Runs multiple specialized AI agents in parallel (scanner, researcher, pattern analyst, forecaster)
- Features a 4-persona adversarial Debate Council for every decision
- Routes ALL decisions — naming, prioritization, architecture, KPIs — through debate
- Targets researchers, engineers, and AI builders who want rigorous multi-agent reasoning
- Is positioned as "not a demo framework — a research instrument"
- Open source, MIT license, targeting GitHub star-worthiness

The name needs to:
1. Be memorable and distinct in the crowded AI tooling space
2. Convey rigor, adversarial testing, and refinement
3. Work as a Python package name (lowercase, no hyphens)
4. Not already be taken on PyPI""",
        options=[
            "crucible — a vessel where materials are tested under extreme heat; the hardest environment forges the strongest results",
            "forge — where raw materials become refined tools; implies craftsmanship and transformation",
            "tribunal — a formal judgment body; emphasizes the adversarial debate at the core",
            "assay — a metallurgical test for quality; precise, scientific, implies rigorous evaluation",
            "crucis — Latin for 'cross' (as in crossroads + crucible); exotic, memorable, hard to spell",
        ],
        verbose=True,
    )

    # Display results as a rich table
    table = Table(title="Debate Council Verdict: Project Name", show_header=True)
    table.add_column("Persona", style="cyan")
    table.add_column("Score", justify="right", style="yellow")
    table.add_column("Rank", justify="center")

    sorted_scores = sorted(result.scores.items(), key=lambda x: -x[1])
    for rank, (persona, score) in enumerate(sorted_scores, 1):
        marker = " 🏆" if persona == result.winner else ""
        table.add_row(persona.title() + marker, f"{score:.1f}/10", str(rank))

    console.print(table)
    console.print()
    console.print(Panel(
        result.decision or "No decision recorded",
        title=f"[bold green]Winner: {result.winner.upper()}[/bold green]",
        border_style="green",
    ))

    if result.dissenting_views:
        console.print("\n[dim]Dissenting views:[/dim]")
        for view in result.dissenting_views:
            console.print(f"  [dim]• {view[:120]}[/dim]")


# ---------------------------------------------------------------------------
# 2. Architecture decision via debate
# ---------------------------------------------------------------------------

async def debate_architecture(orch: Orchestrator) -> None:
    """Example: debate an architecture choice before coding it."""
    console.rule("[bold magenta]Architecture Decision: Agent Communication[/bold magenta]")

    result = await orch.decide(
        topic="How should agents communicate state in a multi-agent research framework?",
        context="We need agents to share findings without creating tight coupling or race conditions.",
        options=[
            "Shared mutable state with async locks (current approach)",
            "Message passing via async queues (actor model)",
            "Event sourcing — all state derived from immutable event log",
            "Blackboard pattern — shared knowledge base agents read/write",
        ],
    )

    console.print(Panel(
        f"Decision: [bold]{result.winner.upper()}[/bold] wins\n\n"
        f"{(result.decision or '')[:400]}",
        title="Architecture Decision",
    ))


# ---------------------------------------------------------------------------
# 3. Full research run
# ---------------------------------------------------------------------------

async def full_research_run(api_key: str, model: str, repo_path: str | None) -> None:
    """Run the complete agent pipeline on a real codebase."""
    console.rule("[bold blue]Full Research Run[/bold blue]")

    subject = "multi-agent AI research frameworks"
    if repo_path:
        subject = f"codebase at {repo_path}"

    orch = Orchestrator(api_key=api_key, model=model)

    console.print(f"[cyan]Subject:[/cyan] {subject}")
    console.print(f"[cyan]Repo:[/cyan] {repo_path or 'none (research only)'}\n")

    state = await orch.run(
        subject=subject,
        repo_path=repo_path,
        research_query="multi-agent AI frameworks: patterns, failures, and emerging approaches",
        run_agents=["scanner", "research", "pattern_analyst", "debate", "forecast"],
    )

    # Print summary
    console.rule("Results")

    if state.get("scan"):
        scan = state["scan"]
        console.print(Panel(
            f"Files: {scan.get('file_count', 0):,}\n"
            f"Lines: {scan.get('total_lines', 0):,}\n"
            f"Languages: {', '.join(list(scan.get('languages', {}).keys())[:5])}\n\n"
            f"{scan.get('summary', '')[:300]}",
            title="Scanner",
        ))

    if state.get("debate"):
        debate = state["debate"]
        console.print(Panel(
            f"Winner: [bold]{debate.get('winner', 'unknown').upper()}[/bold] "
            f"({debate.get('winner_score', 0):.1f}/10)\n\n"
            f"{(debate.get('decision') or '')[:300]}",
            title="Debate Council Verdict",
        ))

    if state.get("forecast"):
        forecast = state["forecast"]
        preds = forecast.get("predictions", [])
        console.print(Panel(
            "\n".join(
                f"• {p.get('claim', str(p))[:100]} ({p.get('probability', '?')}%)"
                for p in preds[:3]
            ),
            title=f"Forecast (confidence: {forecast.get('confidence', 0):.0%})",
        ))

    console.print(f"\n[dim]Full state saved. Run ID: {state.get('run_id', 'N/A')}[/dim]")

    return state


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

async def main() -> None:
    parser = argparse.ArgumentParser(description="Crucible examples")
    parser.add_argument("--api-key", default=os.environ.get("ANTHROPIC_API_KEY"))
    parser.add_argument("--model", default="claude-opus-4-6")
    parser.add_argument("--repo", default=None, help="Path to a git repo to analyze")
    parser.add_argument(
        "--debate-only", action="store_true",
        help="Only run the project naming debate"
    )
    parser.add_argument(
        "--architecture", action="store_true",
        help="Run an architecture decision debate"
    )
    args = parser.parse_args()

    if not args.api_key:
        console.print("[red]Error: Set ANTHROPIC_API_KEY environment variable[/red]")
        console.print("  export ANTHROPIC_API_KEY=sk-...")
        sys.exit(1)

    # Always start with the naming debate — it's the flagship example
    await debate_project_naming(args.api_key, args.model)

    if args.architecture:
        orch = Orchestrator(api_key=args.api_key, model=args.model)
        # Need to init state for standalone decide
        import uuid
        from crucible.core.state import SharedState
        from crucible.core.events import EventBus
        orch._state = SharedState(run_id=str(uuid.uuid4())[:8], subject="architecture")
        orch._bus = EventBus()
        await debate_architecture(orch)

    if not args.debate_only:
        await full_research_run(args.api_key, args.model, args.repo)


if __name__ == "__main__":
    asyncio.run(main())
