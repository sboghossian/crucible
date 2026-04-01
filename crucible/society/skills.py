"""Skill inventory — agents track capabilities, request skills, learn from observations."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class Skill(BaseModel):
    """A single skill entry in an agent's inventory."""

    name: str
    proficiency: float = 0.5    # 0.0–1.0
    source: str = "self"        # "self", "taught:<agent_name>", "observed:<agent_name>"
    acquired_at: datetime = Field(default_factory=datetime.utcnow)
    use_count: int = 0
    last_used: datetime = Field(default_factory=datetime.utcnow)

    def use(self) -> None:
        self.use_count += 1
        self.last_used = datetime.utcnow()
        # Proficiency increases slightly with each use, capped at 1.0
        self.proficiency = round(min(1.0, self.proficiency + 0.01), 4)

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "proficiency": self.proficiency,
            "source": self.source,
            "acquired_at": self.acquired_at.isoformat(),
            "use_count": self.use_count,
            "last_used": self.last_used.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Skill":
        data = dict(data)
        for field in ("acquired_at", "last_used"):
            if isinstance(data.get(field), str):
                data[field] = datetime.fromisoformat(data[field])
        return cls(**data)


class SkillInventory:
    """
    Manages the full skill set for one agent.

    Agents can:
    - Have skills added (self-discovered, taught, or observed)
    - Use skills (raising proficiency over time)
    - Request a skill from a peer (caller is responsible for the transfer)
    - Observe a peer's successful skill use and learn from it
    """

    def __init__(self, agent_id: str) -> None:
        self.agent_id = agent_id
        self._skills: dict[str, Skill] = {}

    def add(self, name: str, source: str = "self", proficiency: float = 0.5) -> Skill:
        """Add or update a skill. If the skill exists, take the higher proficiency."""
        if name in self._skills:
            existing = self._skills[name]
            if proficiency > existing.proficiency:
                existing.proficiency = round(proficiency, 4)
            return existing
        skill = Skill(name=name, source=source, proficiency=proficiency)
        self._skills[name] = skill
        return skill

    def use(self, name: str) -> Skill | None:
        """Record a skill use. Returns None if the agent doesn't have the skill."""
        if name not in self._skills:
            return None
        self._skills[name].use()
        return self._skills[name]

    def observe(self, name: str, observer_agent: str, proficiency: float = 0.3) -> Skill:
        """
        Learn a skill by observing another agent succeed with it.

        Proficiency starts low — mastery comes from repeated use.
        """
        source = f"observed:{observer_agent}"
        return self.add(name, source=source, proficiency=proficiency)

    def receive_teaching(self, name: str, teacher: str, proficiency: float = 0.5) -> Skill:
        """Acquire a skill taught directly by another agent."""
        source = f"taught:{teacher}"
        return self.add(name, source=source, proficiency=proficiency)

    def has(self, name: str) -> bool:
        return name in self._skills

    def get(self, name: str) -> Skill | None:
        return self._skills.get(name)

    def all_skills(self) -> list[Skill]:
        return list(self._skills.values())

    def names(self) -> list[str]:
        return list(self._skills.keys())

    def top_skills(self, n: int = 5) -> list[Skill]:
        return sorted(
            self._skills.values(),
            key=lambda s: s.proficiency,
            reverse=True,
        )[:n]
