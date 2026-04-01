"""
Example: Scan git repos in a directory, run the Debate Council, print results.

Demonstrates:
1. Scanning a directory for git repositories
2. Running the Scanner agent on a real codebase
3. Debate Council deciding "what patterns matter most"
4. Full research pipeline (scanner → research → patterns → debate → forecast)

Usage:
    export ANTHROPIC_API_KEY=sk-...

    # Just run the canonical naming debate:
    python examples/analyze_projects.py --debate-only

    # Scan a directory for git repos and debate patterns:
    python examples/analyze_projects.py --scan-dir ~/projects

    # Analyze a specific repo with a full pipeline run:
    python examples/analyze_projects.py --repo /path/to/repo

    # Run an architecture decision debate:
    python examples/analyze_projects.py --architecture
"""

from __future__ import annotations

import argparse
import asyncio
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from crucible import Orchestrator
from crucible.core.events import EventBus
from crucible.core.state import SharedState

console = Console()
logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(name)s] %(message)s")


# ---------------------------------------------------------------------------
# 1. Find git repos in a directory
# ---------------------------------------------------------------------------


def find_git_repos(directory: str, max_depth: int = 3) -> list[Path]:
    """Walk a directory and return paths of all git repositories found."""
    base = Path(directory).expanduser().resolve()
    if not base.exists():
        console.print(f"[red]Directory not found: {base}[/red]")
        return []

    repos: list[Path] = []
    for item in base.rglob(".git"):
        if item.is_dir():
            repo_path = item.parent
            # Check depth relative to base
            try:
                depth = len(repo_path.relative_to(base).parts)
            except ValueError:
                continue
            if depth <= max_depth:
                repos.append(repo_path)
    return sorted(repos)


# ---------------------------------------------------------------------------
# 2. Project naming debate — the canonical Crucible example
# ---------------------------------------------------------------------------


async def debate_project_naming(api_key: str, model: str) -> None:
    """
    The Debate Council deliberates: what should this framework be named?
    Four personas argue over "crucible" vs four serious alternatives.
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
            "crucible — a vessel where materials are tested under extreme heat; "
            "the hardest environment forges the strongest results",
            "forge — where raw materials become refined tools; implies craftsmanship",
            "tribunal — a formal judgment body; emphasizes the adversarial debate at the core",
            "assay — a metallurgical test for quality; precise, scientific, rigorous evaluation",
            "crucis — Latin for 'cross' (crossroads + crucible); exotic, hard to spell",
        ],
        verbose=True,
    )

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
# 3. Scan a directory and debate which patterns matter most
# ---------------------------------------------------------------------------


async def scan_and_debate_patterns(
    api_key: str, model: str, scan_dir: str
) -> None:
    """
    Find git repos in scan_dir, scan the first one found, then debate
    "what patterns matter most" based on what the Scanner found.
    """
    console.rule("[bold yellow]Scan Directory + Pattern Debate[/bold yellow]")

    repos = find_git_repos(scan_dir)
    if not repos:
        console.print(f"[yellow]No git repositories found in {scan_dir}[/yellow]")
        console.print("Tip: try --repo /path/to/a/specific/repo instead.")
        return

    console.print(f"Found [cyan]{len(repos)}[/cyan] git repo(s) in [cyan]{scan_dir}[/cyan]:")
    for repo in repos[:5]:
        console.print(f"  • {repo}")
    if len(repos) > 5:
        console.print(f"  [dim]... and {len(repos) - 5} more[/dim]")
    console.print()

    # Scan the first repo
    target = repos[0]
    console.print(f"[cyan]Scanning:[/cyan] {target}\n")

    orch = Orchestrator(api_key=api_key, model=model)

    # Initialize state manually so we can call decide() after the scan
    import uuid
    orch._state = SharedState(run_id=str(uuid.uuid4())[:8], subject=str(target.name))
    orch._bus = EventBus()

    scan_result = await orch._run_scanner(str(target))

    if scan_result.success and scan_result.output:
        scan = scan_result.output
        console.print(Panel(
            f"Files: [bold]{scan.get('file_count', 0):,}[/bold]\n"
            f"Lines: [bold]{scan.get('total_lines', 0):,}[/bold]\n"
            f"Languages: [bold]{', '.join(list(scan.get('languages', {}).keys())[:5])}[/bold]\n"
            f"Dependencies: {', '.join(scan.get('dependencies', [])[:3]) or 'none'}\n\n"
            f"[dim]{scan.get('summary', '')[:300]}[/dim]",
            title=f"Scanner: {target.name}",
            border_style="cyan",
        ))
    else:
        console.print(f"[yellow]Scan failed: {scan_result.error}[/yellow]")

    # Debate: what patterns matter most for this codebase?
    console.print("\n[bold]Convening Debate Council on patterns...[/bold]\n")

    state = await orch._state.get()
    context = ""
    if state.scan:
        langs = ", ".join(list(state.scan.languages.keys())[:5])
        context = (
            f"Codebase: {target.name}\n"
            f"Languages: {langs}\n"
            f"Scale: {state.scan.file_count} files, {state.scan.total_lines:,} lines\n"
            f"Summary: {state.scan.summary[:300]}"
        )

    result = await orch.decide(
        topic=f"What software patterns matter most for: {target.name}",
        context=context,
        options=[
            "Architectural patterns (layering, separation of concerns, modularity)",
            "Testing patterns (coverage strategy, integration vs unit, test-first)",
            "Observability patterns (logging, metrics, tracing, error handling)",
            "Developer experience patterns (tooling, onboarding, documentation)",
        ],
    )

    console.print(Panel(
        f"Winner: [bold cyan]{result.winner.upper()}[/bold cyan] "
        f"({result.winner_score:.1f}/10)\n\n"
        f"{(result.decision or '')[:400]}",
        title="What Patterns Matter Most",
        border_style="yellow",
    ))

    if result.dissenting_views:
        console.print("\n[dim]Other perspectives:[/dim]")
        for view in result.dissenting_views[:2]:
            console.print(f"  [dim]• {view[:100]}[/dim]")


# ---------------------------------------------------------------------------
# 4. Architecture decision via debate
# ---------------------------------------------------------------------------


async def debate_architecture(api_key: str, model: str) -> None:
    """Debate an architecture choice using a standalone Debate Council."""
    console.rule("[bold magenta]Architecture Decision: Agent Communication[/bold magenta]")

    orch = Orchestrator(api_key=api_key, model=model)
    result = await orch.standalone_debate(
        topic="How should agents communicate state in a multi-agent research framework?",
        context="We need agents to share findings without tight coupling or race conditions.",
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
        border_style="magenta",
    ))

    # Score table
    table = Table(title="Scores", show_header=True)
    table.add_column("Persona", style="cyan")
    table.add_column("Score", justify="right", style="yellow")
    for persona, score in sorted(result.scores.items(), key=lambda x: -x[1]):
        table.add_row(persona.title(), f"{score:.1f}/10")
    console.print(table)


# ---------------------------------------------------------------------------
# 5. Full research run
# ---------------------------------------------------------------------------


async def full_research_run(
    api_key: str, model: str, repo_path: str | None
) -> dict:
    """Run the complete agent pipeline on a real codebase or topic."""
    console.rule("[bold blue]Full Research Run[/bold blue]")

    subject = "multi-agent AI research frameworks"
    if repo_path:
        subject = f"codebase at {Path(repo_path).name}"

    orch = Orchestrator(api_key=api_key, model=model)

    console.print(f"[cyan]Subject:[/cyan] {subject}")
    console.print(f"[cyan]Repo:[/cyan] {repo_path or 'none (research only)'}\n")

    state = await orch.run(
        subject=subject,
        repo_path=repo_path,
        research_query="multi-agent AI frameworks: patterns, failures, and emerging approaches",
        run_agents=["scanner", "research", "pattern_analyst", "debate", "forecast"],
    )

    console.rule("Results")

    if state.get("scan"):
        scan = state["scan"]
        console.print(Panel(
            f"Files: {scan.get('file_count', 0):,}\n"
            f"Lines: {scan.get('total_lines', 0):,}\n"
            f"Languages: {', '.join(list(scan.get('languages', {}).keys())[:5])}\n\n"
            f"{scan.get('summary', '')[:300]}",
            title="Scanner",
            border_style="cyan",
        ))

    if state.get("research"):
        research = state["research"]
        console.print(Panel(
            f"{research.get('synthesis', '')[:400]}",
            title=f"Research: {research.get('query', '')}",
            border_style="blue",
        ))

    if state.get("debate"):
        debate = state["debate"]
        console.print(Panel(
            f"Winner: [bold]{debate.get('winner', 'unknown').upper()}[/bold] "
            f"({debate.get('winner_score', 0):.1f}/10)\n\n"
            f"{(debate.get('decision') or '')[:300]}",
            title="Debate Council Verdict",
            border_style="green",
        ))

    if state.get("forecast"):
        forecast = state["forecast"]
        preds = forecast.get("predictions", [])
        pred_text = "\n".join(
            f"• {p.get('claim', str(p))[:100]} "
            f"({p.get('probability', '?')}%)"
            for p in preds[:3]
        )
        console.print(Panel(
            pred_text or "No predictions generated.",
            title=f"Forecast (confidence: {forecast.get('confidence', 0):.0%})",
            border_style="yellow",
        ))

    console.print(f"\n[dim]Run ID: {state.get('run_id', 'N/A')}[/dim]")
    return state


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Crucible examples — multi-agent research with adversarial debate",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("ANTHROPIC_API_KEY"),
        help="Anthropic API key (or set ANTHROPIC_API_KEY env var)",
    )
    parser.add_argument(
        "--model",
        default="claude-opus-4-6",
        help="Claude model to use (default: claude-opus-4-6)",
    )
    parser.add_argument(
        "--repo",
        default=None,
        help="Path to a specific git repo to analyze",
    )
    parser.add_argument(
        "--scan-dir",
        default=None,
        help="Directory to scan for git repos; debates patterns in the first one found",
    )
    parser.add_argument(
        "--debate-only",
        action="store_true",
        help="Only run the project naming debate, then exit",
    )
    parser.add_argument(
        "--architecture",
        action="store_true",
        help="Run the architecture decision debate",
    )
    args = parser.parse_args()

    if not args.api_key:
        console.print("[red]Error: Anthropic API key required.[/red]")
        console.print("  export ANTHROPIC_API_KEY=sk-ant-...")
        console.print("  or pass --api-key sk-ant-...")
        sys.exit(1)

    # The canonical naming debate always runs first
    await debate_project_naming(args.api_key, args.model)

    if args.debate_only:
        return

    if args.scan_dir:
        await scan_and_debate_patterns(args.api_key, args.model, args.scan_dir)
        return

    if args.architecture:
        await debate_architecture(args.api_key, args.model)
        return

    # Default: full research run
    await full_research_run(args.api_key, args.model, args.repo)


if __name__ == "__main__":
    asyncio.run(main())
