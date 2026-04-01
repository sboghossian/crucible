"""Emergent compression tokens — agent pairs develop shorthand for frequent concepts."""

from __future__ import annotations

import hashlib
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

# A token becomes stable after this many uses
ADOPTION_THRESHOLD = 10
# Token decays (becomes inactive) if unused for this many cycles
DECAY_CYCLES = 50


class CompressionToken(BaseModel):
    """
    A shorthand symbol developed by an agent pair for a recurring concept.

    Tokens are:
    - Generated when a concept has been exchanged >= ADOPTION_THRESHOLD times
    - Decompressible (the full meaning is always stored)
    - Logged for research into emergent communication
    """

    token_id: str
    agent_a: str
    agent_b: str
    concept: str           # full natural-language description
    token: str             # shorthand symbol, e.g. "⟨arch-debate⟩"
    use_count: int = 0
    is_active: bool = False
    last_used_cycle: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def decompress(self) -> str:
        """Return the full meaning of this token."""
        return self.concept

    def use(self, cycle: int) -> None:
        self.use_count += 1
        self.last_used_cycle = cycle
        if self.use_count >= ADOPTION_THRESHOLD:
            self.is_active = True

    def is_decayed(self, current_cycle: int) -> bool:
        return self.is_active and (current_cycle - self.last_used_cycle) > DECAY_CYCLES

    def to_dict(self) -> dict[str, Any]:
        return {
            "token_id": self.token_id,
            "agent_a": self.agent_a,
            "agent_b": self.agent_b,
            "concept": self.concept,
            "token": self.token,
            "use_count": self.use_count,
            "is_active": self.is_active,
            "last_used_cycle": self.last_used_cycle,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CompressionToken":
        data = dict(data)
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        return cls(**data)


def _make_token_symbol(agent_a: str, agent_b: str, concept: str) -> str:
    """Deterministically derive a short symbol from the concept + pair."""
    raw = f"{agent_a}:{agent_b}:{concept}"
    h = hashlib.sha1(raw.encode()).hexdigest()[:6]
    return f"⟨{h}⟩"


def _make_token_id(agent_a: str, agent_b: str, concept: str) -> str:
    raw = f"{agent_a}|{agent_b}|{concept}"
    return hashlib.sha1(raw.encode()).hexdigest()[:12]


class EmergentLanguage:
    """
    Tracks compression tokens for all agent pairs.

    Usage:
        lang = EmergentLanguage()
        token = lang.exchange(agent_a, agent_b, concept, cycle=1)
        if token.is_active:
            # use token.token as shorthand
            full_meaning = token.decompress()
    """

    def __init__(self) -> None:
        self._tokens: dict[str, CompressionToken] = {}

    def exchange(
        self, agent_a: str, agent_b: str, concept: str, cycle: int = 0
    ) -> CompressionToken:
        """
        Record an exchange of `concept` between the agent pair and return the token.

        The pair is normalised (sorted) so A↔B and B↔A share the same token.
        """
        a, b = sorted([agent_a, agent_b])
        token_id = _make_token_id(a, b, concept)

        if token_id not in self._tokens:
            self._tokens[token_id] = CompressionToken(
                token_id=token_id,
                agent_a=a,
                agent_b=b,
                concept=concept,
                token=_make_token_symbol(a, b, concept),
            )

        tok = self._tokens[token_id]
        tok.use(cycle)
        return tok

    def active_tokens(self) -> list[CompressionToken]:
        return [t for t in self._tokens.values() if t.is_active]

    def prune_decayed(self, current_cycle: int) -> list[CompressionToken]:
        """Mark decayed tokens inactive and return the pruned list."""
        pruned = []
        for tok in self._tokens.values():
            if tok.is_decayed(current_cycle):
                tok.is_active = False
                pruned.append(tok)
        return pruned

    def all_tokens(self) -> list[CompressionToken]:
        return list(self._tokens.values())
