"""Crucible debate subsystem."""

from .personas import ALL_PERSONAS, PERSONA_BY_NAME, Persona
from .protocol import DebateProtocol, DebateTranscript, Statement
from .resolver import Resolution, format_summary, resolve, to_debate_result

__all__ = [
    "ALL_PERSONAS",
    "PERSONA_BY_NAME",
    "Persona",
    "DebateProtocol",
    "DebateTranscript",
    "Statement",
    "Resolution",
    "format_summary",
    "resolve",
    "to_debate_result",
]
