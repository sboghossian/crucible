"""Streaming output for real-time debate viewing."""

from .events import (
    DebateEvent,
    DebateStarted,
    PersonaThinking,
    ArgumentSubmitted,
    CrossExamination,
    ScoringStarted,
    ScoringComplete,
    WinnerDeclared,
)
from .stream import DebateStream
from .renderer import DebateRenderer

__all__ = [
    "DebateEvent",
    "DebateStarted",
    "PersonaThinking",
    "ArgumentSubmitted",
    "CrossExamination",
    "ScoringStarted",
    "ScoringComplete",
    "WinnerDeclared",
    "DebateStream",
    "DebateRenderer",
]
