"""Persistent agent identity with XP, level, and personality traits."""

from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class Level(str, Enum):
    NOVICE = "Novice"
    APPRENTICE = "Apprentice"
    JOURNEYMAN = "Journeyman"
    EXPERT = "Expert"
    MASTER = "Master"


_LEVEL_THRESHOLDS: list[tuple[int, Level]] = [
    (10_000, Level.MASTER),
    (2_000, Level.EXPERT),
    (500, Level.JOURNEYMAN),
    (100, Level.APPRENTICE),
    (0, Level.NOVICE),
]


def xp_to_level(xp: int) -> Level:
    for threshold, level in _LEVEL_THRESHOLDS:
        if xp >= threshold:
            return level
    return Level.NOVICE


class AgentIdentity(BaseModel):
    """
    Persistent identity for a Crucible agent.

    The `creator` field is immutable and anchors every agent back to
    its originating human — part of the alignment spec's safety-as-physics
    approach.
    """

    agent_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    agent_type: str = "generic"
    creator: str = "Steph"  # immutable creator anchor — alignment spec §5.3

    # XP economy
    xp: int = 0

    # Personality traits (0.0–1.0 each)
    traits: dict[str, float] = Field(
        default_factory=lambda: {
            "curiosity": 0.5,
            "caution": 0.5,
            "creativity": 0.5,
            "precision": 0.5,
            "collaboration": 0.5,
            "independence": 0.5,
        }
    )

    # Skill inventory — list of skill names this agent has acquired
    skill_names: list[str] = Field(default_factory=list)

    # Metadata
    created_at: datetime = Field(default_factory=datetime.utcnow)
    last_active: datetime = Field(default_factory=datetime.utcnow)

    @property
    def level(self) -> Level:
        return xp_to_level(self.xp)

    @property
    def xp_to_next_level(self) -> int | None:
        """XP remaining until next level, or None if Master."""
        thresholds = [100, 500, 2_000, 10_000]
        for t in thresholds:
            if self.xp < t:
                return t - self.xp
        return None  # already Master

    def add_xp(self, amount: int) -> int:
        """Add XP and return new total."""
        self.xp = max(0, self.xp + amount)
        self.last_active = datetime.utcnow()
        return self.xp

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "agent_type": self.agent_type,
            "creator": self.creator,
            "xp": self.xp,
            "level": self.level.value,
            "traits": self.traits,
            "skill_names": self.skill_names,
            "created_at": self.created_at.isoformat(),
            "last_active": self.last_active.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentIdentity":
        data = dict(data)
        data.pop("level", None)  # computed property, not stored
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if isinstance(data.get("last_active"), str):
            data["last_active"] = datetime.fromisoformat(data["last_active"])
        return cls(**data)
