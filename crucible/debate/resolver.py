"""Determines winner, records decision, and formats the debate summary."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .protocol import DebateTranscript
from ..core.state import DebateResult


@dataclass
class Resolution:
    topic: str
    winner: str
    winner_score: float
    decision: str
    scores: dict[str, float]
    dissenting_views: list[str]
    rounds_summary: list[dict[str, Any]]
    recommendation: str


def resolve(transcript: DebateTranscript) -> Resolution:
    """Convert a DebateTranscript into a Resolution with a clean recommendation."""

    # Build rounds summary
    rounds_summary: list[dict[str, Any]] = []
    for round_num in [1, 2, 3]:
        round_stmts = [s for s in transcript.statements if s.round == round_num]
        rounds_summary.append({
            "round": round_num,
            "statements": [
                {
                    "persona": s.persona_name,
                    "content": s.content,
                    "targets": s.targets,
                }
                for s in round_stmts
            ],
        })

    # Extract the recommendation from the winner's closing statement
    winning_closing = next(
        (
            s for s in transcript.statements
            if s.round == 3 and s.persona_name == transcript.winner
        ),
        None,
    )
    recommendation = ""
    if winning_closing:
        # First non-empty, non-header line after "Closing argument:"
        lines = [l.strip() for l in winning_closing.content.split("\n") if l.strip()]
        for line in lines:
            if not line.lower().startswith("closing argument"):
                recommendation = line
                break

    return Resolution(
        topic=transcript.topic,
        winner=transcript.winner,
        winner_score=transcript.winner_score,
        decision=transcript.decision,
        scores=transcript.scores,
        dissenting_views=transcript.dissenting_views,
        rounds_summary=rounds_summary,
        recommendation=recommendation,
    )


def to_debate_result(transcript: DebateTranscript) -> DebateResult:
    """Convert transcript to a DebateResult for shared state storage."""
    resolution = resolve(transcript)
    return DebateResult(
        topic=transcript.topic,
        winner=resolution.winner,
        winner_score=resolution.winner_score,
        decision=resolution.decision,
        rounds=resolution.rounds_summary,
        scores=resolution.scores,
        dissenting_views=resolution.dissenting_views,
    )


def format_summary(resolution: Resolution, verbose: bool = False) -> str:
    """Return a human-readable summary of the debate outcome."""
    score_line = "  ".join(
        f"{name}: {score:.1f}"
        for name, score in sorted(resolution.scores.items(), key=lambda x: -x[1])
    )

    lines = [
        f"DEBATE: {resolution.topic}",
        "─" * 60,
        f"WINNER: {resolution.winner.upper()} (score: {resolution.winner_score:.1f}/10)",
        f"SCORES: {score_line}",
        "",
        "DECISION:",
        resolution.recommendation or resolution.decision[:500],
    ]

    if resolution.dissenting_views:
        lines += ["", "DISSENTING VIEWS:"]
        for view in resolution.dissenting_views:
            lines.append(f"  • {view}")

    if verbose:
        lines += ["", "─" * 60, "FULL TRANSCRIPT:"]
        for round_data in resolution.rounds_summary:
            rn = round_data["round"]
            label = {1: "OPENING STATEMENTS", 2: "CROSS-EXAMINATION", 3: "CLOSING ARGUMENTS"}[rn]
            lines += [f"\n[ROUND {rn}: {label}]"]
            for stmt in round_data["statements"]:
                lines += [f"\n{stmt['persona'].upper()}:", stmt["content"]]

    return "\n".join(lines)
