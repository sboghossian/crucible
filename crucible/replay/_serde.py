"""Event serialization / deserialization utilities for replay."""

from __future__ import annotations

import dataclasses
import json
from typing import Any

from ..streaming.events import (
    ArgumentSubmitted,
    CrossExamination,
    DebateEvent,
    DebateStarted,
    PersonaThinking,
    ScoringComplete,
    ScoringStarted,
    WinnerDeclared,
)

_KIND_TO_CLASS: dict[str, type] = {
    "debate_started": DebateStarted,
    "persona_thinking": PersonaThinking,
    "argument_submitted": ArgumentSubmitted,
    "cross_examination": CrossExamination,
    "scoring_started": ScoringStarted,
    "scoring_complete": ScoringComplete,
    "winner_declared": WinnerDeclared,
}


def event_to_json(event: DebateEvent) -> str:
    return json.dumps(dataclasses.asdict(event))


def event_from_row(row: dict[str, Any]) -> DebateEvent:
    d: dict[str, Any] = json.loads(row["event_json"])
    kind: str = row["event_kind"]
    cls = _KIND_TO_CLASS.get(kind)
    if cls is None:
        raise ValueError(f"Unknown event kind: {kind!r}")
    init_fields = {f.name for f in dataclasses.fields(cls) if f.init}  # type: ignore[arg-type]
    kwargs = {k: v for k, v in d.items() if k in init_fields}
    return cls(**kwargs)  # type: ignore[return-value]


def event_round(event: DebateEvent) -> int:
    """Return the debate round number for an event (0=header, 4=post-debate)."""
    r = getattr(event, "round", None)
    if r is not None:
        return int(r)
    if event.kind == "cross_examination":
        return 2
    if event.kind in ("scoring_started", "scoring_complete", "winner_declared"):
        return 4
    return 0  # debate_started
