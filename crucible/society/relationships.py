"""Agent relationship tracking — trust scores, collaboration history, autonomous teams."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

AUTONOMOUS_TEAM_THRESHOLD = 0.7  # trust score above which agents can self-organise
TRUST_SUCCESS_DELTA = 0.05
TRUST_FAILURE_DELTA = -0.08
TRUST_MIN = 0.0
TRUST_MAX = 1.0


class AgentRelationship(BaseModel):
    """
    Directed relationship from `agent_id` → `peer_id`.

    Trust is domain-agnostic; future versions may add per-domain trust.
    """

    agent_id: str
    peer_id: str
    trust: float = 0.5
    collaboration_count: int = 0
    success_count: int = 0
    last_interaction: datetime = Field(default_factory=datetime.utcnow)

    @property
    def success_rate(self) -> float:
        if self.collaboration_count == 0:
            return 0.0
        return self.success_count / self.collaboration_count

    @property
    def can_form_team(self) -> bool:
        return self.trust >= AUTONOMOUS_TEAM_THRESHOLD

    def record_interaction(self, success: bool) -> None:
        self.collaboration_count += 1
        if success:
            self.success_count += 1
            self.trust = round(
                min(TRUST_MAX, self.trust + TRUST_SUCCESS_DELTA), 4
            )
        else:
            self.trust = round(
                max(TRUST_MIN, self.trust + TRUST_FAILURE_DELTA), 4
            )
        self.last_interaction = datetime.utcnow()

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "peer_id": self.peer_id,
            "trust": self.trust,
            "collaboration_count": self.collaboration_count,
            "success_count": self.success_count,
            "success_rate": self.success_rate,
            "can_form_team": self.can_form_team,
            "last_interaction": self.last_interaction.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentRelationship":
        data = dict(data)
        data.pop("success_rate", None)
        data.pop("can_form_team", None)
        if isinstance(data.get("last_interaction"), str):
            data["last_interaction"] = datetime.fromisoformat(data["last_interaction"])
        return cls(**data)


class RelationshipGraph:
    """
    In-memory graph of all agent relationships.

    Keyed by (agent_id, peer_id) pairs. Symmetric pairs are stored separately
    to allow asymmetric trust (A trusts B ≠ B trusts A).
    """

    def __init__(self) -> None:
        self._edges: dict[tuple[str, str], AgentRelationship] = {}

    def get(self, agent_id: str, peer_id: str) -> AgentRelationship:
        key = (agent_id, peer_id)
        if key not in self._edges:
            self._edges[key] = AgentRelationship(
                agent_id=agent_id, peer_id=peer_id
            )
        return self._edges[key]

    def record(self, agent_id: str, peer_id: str, success: bool) -> AgentRelationship:
        """Record a collaboration outcome and return the updated relationship."""
        rel = self.get(agent_id, peer_id)
        rel.record_interaction(success)
        return rel

    def autonomous_teams(self) -> list[tuple[str, str]]:
        """Return all (agent, peer) pairs with trust >= threshold."""
        return [
            (rel.agent_id, rel.peer_id)
            for rel in self._edges.values()
            if rel.can_form_team
        ]

    def all_relationships(self) -> list[AgentRelationship]:
        return list(self._edges.values())
