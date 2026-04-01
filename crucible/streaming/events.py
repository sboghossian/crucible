"""Typed streaming events for real-time debate output."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Union


@dataclass
class DebateStarted:
    kind: Literal["debate_started"] = field(default="debate_started", init=False)
    topic: str = ""
    context: str = ""
    options: list[str] = field(default_factory=list)


@dataclass
class PersonaThinking:
    kind: Literal["persona_thinking"] = field(default="persona_thinking", init=False)
    persona_name: str = ""
    round: int = 0
    round_label: str = ""


@dataclass
class ArgumentSubmitted:
    kind: Literal["argument_submitted"] = field(default="argument_submitted", init=False)
    persona_name: str = ""
    round: int = 0
    round_label: str = ""
    content: str = ""
    targets: list[str] = field(default_factory=list)


@dataclass
class CrossExamination:
    kind: Literal["cross_examination"] = field(default="cross_examination", init=False)
    persona_name: str = ""
    content: str = ""
    targets: list[str] = field(default_factory=list)


@dataclass
class ScoringStarted:
    kind: Literal["scoring_started"] = field(default="scoring_started", init=False)


@dataclass
class ScoringComplete:
    kind: Literal["scoring_complete"] = field(default="scoring_complete", init=False)
    scores: dict[str, float] = field(default_factory=dict)


@dataclass
class WinnerDeclared:
    kind: Literal["winner_declared"] = field(default="winner_declared", init=False)
    winner: str = ""
    winner_score: float = 0.0
    decision: str = ""
    dissenting_views: list[str] = field(default_factory=list)


DebateEvent = Union[
    DebateStarted,
    PersonaThinking,
    ArgumentSubmitted,
    CrossExamination,
    ScoringStarted,
    ScoringComplete,
    WinnerDeclared,
]

ROUND_LABELS = {1: "Opening Statement", 2: "Cross-Examination", 3: "Closing Argument"}
