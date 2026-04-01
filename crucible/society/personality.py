"""Personality drift — traits shift gradually based on task outcomes and collaboration."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

TRAIT_NAMES: list[str] = [
    "curiosity",
    "caution",
    "creativity",
    "precision",
    "collaboration",
    "independence",
]

MAX_DRIFT_PER_CYCLE = 0.02
TRAIT_MIN = 0.0
TRAIT_MAX = 1.0


class PersonalitySnapshot(BaseModel):
    """A point-in-time record of an agent's traits."""
    agent_id: str
    traits: dict[str, float]
    cycle: int = 0
    reason: str = ""
    recorded_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "traits": self.traits,
            "cycle": self.cycle,
            "reason": self.reason,
            "recorded_at": self.recorded_at.isoformat(),
        }


class PersonalityDrift:
    """
    Computes trait deltas for a single drift cycle.

    Rules (safety-as-physics):
    - Each trait can move at most MAX_DRIFT_PER_CYCLE (0.02) per cycle.
    - Traits are clamped to [0.0, 1.0].
    - Drift direction is determined by task outcomes and collaboration patterns.
    """

    @staticmethod
    def compute_drift(
        current_traits: dict[str, float],
        task_succeeded: bool,
        collaborated: bool,
        novel_approach: bool = False,
    ) -> dict[str, float]:
        """
        Return new trait dict after one drift cycle.

        Args:
            current_traits: Current trait values.
            task_succeeded: Whether the agent's task completed successfully.
            collaborated: Whether the agent worked with another agent.
            novel_approach: Whether the agent tried something new.
        """
        deltas: dict[str, float] = {t: 0.0 for t in TRAIT_NAMES}

        if task_succeeded:
            # Success reinforces the approach taken
            if novel_approach:
                deltas["curiosity"] += MAX_DRIFT_PER_CYCLE
                deltas["creativity"] += MAX_DRIFT_PER_CYCLE
                deltas["caution"] -= MAX_DRIFT_PER_CYCLE * 0.5
            else:
                deltas["precision"] += MAX_DRIFT_PER_CYCLE
                deltas["caution"] += MAX_DRIFT_PER_CYCLE * 0.5
        else:
            # Failure nudges toward caution and precision
            deltas["caution"] += MAX_DRIFT_PER_CYCLE
            deltas["curiosity"] -= MAX_DRIFT_PER_CYCLE * 0.5
            deltas["precision"] += MAX_DRIFT_PER_CYCLE * 0.5

        if collaborated:
            deltas["collaboration"] += MAX_DRIFT_PER_CYCLE
            deltas["independence"] -= MAX_DRIFT_PER_CYCLE * 0.5
        else:
            deltas["independence"] += MAX_DRIFT_PER_CYCLE * 0.5
            deltas["collaboration"] -= MAX_DRIFT_PER_CYCLE * 0.25

        new_traits: dict[str, float] = {}
        for trait in TRAIT_NAMES:
            raw = current_traits.get(trait, 0.5) + deltas.get(trait, 0.0)
            new_traits[trait] = round(
                max(TRAIT_MIN, min(TRAIT_MAX, raw)), 4
            )
        return new_traits

    @staticmethod
    def max_change(old: dict[str, float], new: dict[str, float]) -> float:
        """Return the largest absolute trait change across all traits."""
        return max(
            abs(new.get(t, 0.5) - old.get(t, 0.5)) for t in TRAIT_NAMES
        )
