"""Records debate streaming events to SQLite for later replay."""

from __future__ import annotations

import time
import uuid
from typing import AsyncIterator

from ..memory.sqlite_store import SQLiteMemoryStore
from ..streaming.events import DebateEvent
from ._serde import event_round, event_to_json


class DebateRecorder:
    """
    Wraps a debate event stream and persists every event to SQLite.

    Usage::

        recorder = DebateRecorder(store)
        debate_id = recorder.new_session(topic, context, options, personas)
        stream = DebateStream(client, model)
        async for event in recorder.record(debate_id, stream.run(topic)):
            renderer.render(event)
    """

    def __init__(self, store: SQLiteMemoryStore) -> None:
        self._store = store

    def new_session(
        self,
        topic: str,
        context: str = "",
        options: list[str] | None = None,
        personas: list[str] | None = None,
        debate_id: str | None = None,
        parent_debate_id: str | None = None,
        branch_round: int | None = None,
        new_prompt: str | None = None,
    ) -> str:
        """Create a session record and return the debate_id."""
        sid = debate_id or str(uuid.uuid4())
        self._store.save_debate_session(
            session_id=sid,
            topic=topic,
            context=context or "",
            options=options or [],
            personas=personas or [],
            parent_debate_id=parent_debate_id,
            branch_round=branch_round,
            new_prompt=new_prompt,
        )
        return sid

    async def record(
        self,
        debate_id: str,
        stream_gen: AsyncIterator[DebateEvent],
    ) -> AsyncIterator[DebateEvent]:
        """
        Async generator: records each event to SQLite and yields it unchanged.
        Marks the session complete when the stream is exhausted.
        """
        start = time.monotonic()
        seq = 0
        try:
            async for event in stream_gen:
                elapsed_ms = int((time.monotonic() - start) * 1000)
                self._store.save_debate_event(
                    debate_id=debate_id,
                    seq=seq,
                    round_number=event_round(event),
                    persona=getattr(event, "persona_name", ""),
                    event_kind=event.kind,
                    event_json=event_to_json(event),
                    elapsed_ms=elapsed_ms,
                )
                seq += 1
                yield event
        finally:
            self._store.mark_debate_session_complete(debate_id, seq)
