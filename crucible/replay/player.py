"""Replays recorded debate sessions from SQLite."""

from __future__ import annotations

import asyncio
from typing import AsyncIterator

from ..memory.sqlite_store import SQLiteMemoryStore
from ..streaming.events import DebateEvent
from ._serde import event_from_row


class DebatePlayer:
    """
    Replays a recorded debate session, optionally starting from a specific round.

    Usage::

        player = DebatePlayer(store)
        async for event in player.replay(debate_id, speed=2.0):
            renderer.render(event)
    """

    INSTANT: float = float("inf")

    def __init__(self, store: SQLiteMemoryStore) -> None:
        self._store = store

    async def replay(
        self,
        debate_id: str,
        speed: float = 1.0,
    ) -> AsyncIterator[DebateEvent]:
        """Replay all events for a debate with optional speed multiplier."""
        rows = self._store.get_debate_events(debate_id)
        async for event in self._emit(rows, speed):
            yield event

    async def replay_from(
        self,
        debate_id: str,
        round_number: int,
        speed: float = 1.0,
    ) -> AsyncIterator[DebateEvent]:
        """Replay events starting from round_number (DebateStarted always included)."""
        rows = self._store.get_debate_events(debate_id, from_round=round_number)
        async for event in self._emit(rows, speed):
            yield event

    async def _emit(
        self,
        rows: list[dict],
        speed: float,
    ) -> AsyncIterator[DebateEvent]:
        prev_elapsed = 0
        for row in rows:
            if speed != self.INSTANT and speed > 0:
                delay = (row["elapsed_ms"] - prev_elapsed) / 1000.0 / speed
                if delay > 0.01:
                    await asyncio.sleep(delay)
            prev_elapsed = row["elapsed_ms"]
            yield event_from_row(row)
