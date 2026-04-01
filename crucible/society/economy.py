"""XP economy for the Agent Society."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class XPEvent(str, Enum):
    """All events that generate (or cost) XP."""
    TEACHING = "teaching"            # +20: taught another agent a skill
    LEARNING = "learning"            # +5:  learned from another agent
    TASK_SUCCESS = "task_success"    # +10: completed a task in skill domain
    TASK_FAILURE = "task_failure"    # +0:  failed a task (no penalty)
    DEBATE_WIN = "debate_win"        # +8:  won a debate round
    ACCURATE_PREDICTION = "accurate_prediction"   # +8: prediction confirmed
    INACCURATE_PREDICTION = "inaccurate_prediction"  # -2: prediction wrong
    NOVEL_TOKEN_ADOPTED = "novel_token_adopted"   # +15: compression token adopted


XP_REWARDS: dict[XPEvent, int] = {
    XPEvent.TEACHING: 20,
    XPEvent.LEARNING: 5,
    XPEvent.TASK_SUCCESS: 10,
    XPEvent.TASK_FAILURE: 0,
    XPEvent.DEBATE_WIN: 8,
    XPEvent.ACCURATE_PREDICTION: 8,
    XPEvent.INACCURATE_PREDICTION: -2,
    XPEvent.NOVEL_TOKEN_ADOPTED: 15,
}


class XPTransaction(BaseModel):
    """An immutable record of a single XP award or deduction."""
    agent_id: str
    event: XPEvent
    amount: int
    balance_after: int
    context: str = ""
    occurred_at: datetime = Field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        return {
            "agent_id": self.agent_id,
            "event": self.event.value,
            "amount": self.amount,
            "balance_after": self.balance_after,
            "context": self.context,
            "occurred_at": self.occurred_at.isoformat(),
        }


class XPEconomy:
    """
    Stateless helper that computes XP awards and records transactions.

    Callers are responsible for persisting the resulting XPTransaction
    via SocietyStore.
    """

    @staticmethod
    def award(event: XPEvent, context: str = "") -> int:
        """Return the XP delta for a given event."""
        return XP_REWARDS[event]

    @staticmethod
    def compute_transaction(
        agent_id: str,
        event: XPEvent,
        current_balance: int,
        context: str = "",
    ) -> XPTransaction:
        """Create an XPTransaction for the given event."""
        amount = XP_REWARDS[event]
        new_balance = max(0, current_balance + amount)
        return XPTransaction(
            agent_id=agent_id,
            event=event,
            amount=amount,
            balance_after=new_balance,
            context=context,
        )
