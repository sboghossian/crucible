"""Rich-based terminal renderer for live debate display."""

from __future__ import annotations

from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.spinner import Spinner
from rich.table import Table
from rich.text import Text

from .events import (
    ArgumentSubmitted,
    CrossExamination,
    DebateEvent,
    DebateStarted,
    PersonaThinking,
    ScoringComplete,
    ScoringStarted,
    WinnerDeclared,
)

# Color per persona — consistent throughout the debate
PERSONA_COLORS: dict[str, str] = {
    "pragmatist": "blue",
    "visionary": "green",
    "skeptic": "red",
    "user_advocate": "yellow",
}

PERSONA_LABELS: dict[str, str] = {
    "pragmatist": "The Pragmatist",
    "visionary": "The Visionary",
    "skeptic": "The Skeptic",
    "user_advocate": "The User Advocate",
}

ROUND_HEADERS: dict[int, str] = {
    1: "ROUND 1 — OPENING STATEMENTS",
    2: "ROUND 2 — CROSS-EXAMINATION",
    3: "ROUND 3 — CLOSING ARGUMENTS",
}


def _persona_label(name: str) -> str:
    return PERSONA_LABELS.get(name, name.replace("_", " ").title())


def _persona_color(name: str) -> str:
    return PERSONA_COLORS.get(name, "white")


class DebateRenderer:
    """
    Handles rendering of DebateEvent objects to a Rich console.

    Can be used with Rich Live for real-time updates, or standalone
    (each event printed immediately).
    """

    def __init__(self, console: Console | None = None) -> None:
        self._console = console or Console()
        self._current_round: int = 0
        self._seen_rounds: set[int] = set()

    def render(self, event: DebateEvent) -> None:
        """Render a single event to the console."""
        if isinstance(event, DebateStarted):
            self._render_debate_started(event)
        elif isinstance(event, PersonaThinking):
            self._render_persona_thinking(event)
        elif isinstance(event, ArgumentSubmitted):
            self._render_argument(event)
        elif isinstance(event, CrossExamination):
            self._render_cross_examination(event)
        elif isinstance(event, ScoringStarted):
            self._render_scoring_started()
        elif isinstance(event, ScoringComplete):
            self._render_scoring_complete(event)
        elif isinstance(event, WinnerDeclared):
            self._render_winner(event)

    def _render_debate_started(self, event: DebateStarted) -> None:
        options_text = "\n".join(f"  • {o}" for o in event.options) if event.options else "  Open-ended"
        body = f"[bold]Topic:[/bold] [cyan]{event.topic}[/cyan]"
        if event.context:
            body += f"\n[dim]Context:[/dim] {event.context[:200]}"
        body += f"\n\n[bold]Options:[/bold]\n{options_text}"
        self._console.print(Panel(body, title="[bold cyan]Crucible Debate Council[/bold cyan]", border_style="cyan"))
        self._console.print()

    def _maybe_print_round_header(self, round_num: int) -> None:
        if round_num not in self._seen_rounds:
            self._seen_rounds.add(round_num)
            header = ROUND_HEADERS.get(round_num, f"ROUND {round_num}")
            self._console.print(f"\n[bold white on dark_blue] {header} [/bold white on dark_blue]\n")

    def _render_persona_thinking(self, event: PersonaThinking) -> None:
        self._maybe_print_round_header(event.round)
        color = _persona_color(event.persona_name)
        label = _persona_label(event.persona_name)
        self._console.print(f"  [{color}]⟳ {label}[/{color}] [dim]is thinking...[/dim]")

    def _render_argument(self, event: ArgumentSubmitted) -> None:
        color = _persona_color(event.persona_name)
        label = _persona_label(event.persona_name)
        title = f"[bold {color}]{label}[/bold {color}] — {event.round_label}"
        self._console.print(Panel(event.content, title=title, border_style=color))
        self._console.print()

    def _render_cross_examination(self, event: CrossExamination) -> None:
        self._maybe_print_round_header(2)
        color = _persona_color(event.persona_name)
        label = _persona_label(event.persona_name)
        title = f"[bold {color}]{label}[/bold {color}] — Cross-Examination"
        if event.targets:
            targets_str = ", ".join(_persona_label(t) for t in event.targets)
            title += f" [dim](challenges: {targets_str})[/dim]"
        self._console.print(Panel(event.content, title=title, border_style=color))
        self._console.print()

    def _render_scoring_started(self) -> None:
        self._console.print("\n[bold white on dark_blue] SCORING [/bold white on dark_blue]")
        self._console.print("[dim]  Computing scores across 4 criteria...[/dim]")

    def _render_scoring_complete(self, event: ScoringComplete) -> None:
        table = Table(title="Scores", show_header=True, header_style="bold magenta")
        table.add_column("Persona", style="bold")
        table.add_column("Score", justify="right")
        table.add_column("", no_wrap=True)

        ranked = sorted(event.scores.items(), key=lambda x: -x[1])
        for i, (name, score) in enumerate(ranked):
            color = _persona_color(name)
            bar = "█" * int(score) + "░" * (10 - int(score))
            medal = " 🥇" if i == 0 else ""
            table.add_row(
                f"[{color}]{_persona_label(name)}[/{color}]{medal}",
                f"[bold]{score:.1f}[/bold]/10",
                f"[{color}]{bar}[/{color}]",
            )
        self._console.print(table)
        self._console.print()

    def _render_winner(self, event: WinnerDeclared) -> None:
        color = _persona_color(event.winner)
        label = _persona_label(event.winner)
        body = (
            f"[bold {color}]{label}[/bold {color}] wins with score "
            f"[bold]{event.winner_score:.1f}/10[/bold]\n\n"
        )
        if event.decision:
            # Strip the bracketed preamble added by protocol
            decision_text = event.decision
            if decision_text.startswith("["):
                end = decision_text.find("]")
                if end != -1:
                    decision_text = decision_text[end + 1:].strip()
            body += decision_text[:600]
            if len(decision_text) > 600:
                body += "\n[dim]...[/dim]"

        if event.dissenting_views:
            body += "\n\n[bold]Dissenting views:[/bold]"
            for view in event.dissenting_views:
                body += f"\n  [dim]• {view[:120]}[/dim]"

        self._console.print(
            Panel(body, title="[bold green] WINNER DECLARED [/bold green]", border_style="green")
        )
