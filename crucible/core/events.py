"""Event bus for agent communication."""

from __future__ import annotations

import asyncio
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Coroutine
import logging

logger = logging.getLogger(__name__)


class EventType(str, Enum):
    AGENT_STARTED = "agent.started"
    AGENT_COMPLETED = "agent.completed"
    AGENT_FAILED = "agent.failed"
    AGENT_OUTPUT = "agent.output"
    DEBATE_ROUND_STARTED = "debate.round.started"
    DEBATE_ROUND_COMPLETED = "debate.round.completed"
    DEBATE_COMPLETED = "debate.completed"
    MEMORY_STORED = "memory.stored"
    ORCHESTRATOR_STARTED = "orchestrator.started"
    ORCHESTRATOR_COMPLETED = "orchestrator.completed"
    STATE_UPDATED = "state.updated"


@dataclass
class Event:
    type: EventType
    source: str
    payload: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    run_id: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "type": self.type.value,
            "source": self.source,
            "payload": self.payload,
            "timestamp": self.timestamp.isoformat(),
            "run_id": self.run_id,
        }


Handler = Callable[[Event], Coroutine[Any, Any, None]]


class EventBus:
    """Async publish-subscribe event bus for agent communication."""

    def __init__(self) -> None:
        self._handlers: dict[EventType, list[Handler]] = defaultdict(list)
        self._wildcard_handlers: list[Handler] = []
        self._history: list[Event] = []
        self._lock = asyncio.Lock()

    def subscribe(self, event_type: EventType, handler: Handler) -> None:
        self._handlers[event_type].append(handler)

    def subscribe_all(self, handler: Handler) -> None:
        """Subscribe to every event type."""
        self._wildcard_handlers.append(handler)

    def unsubscribe(self, event_type: EventType, handler: Handler) -> None:
        handlers = self._handlers[event_type]
        if handler in handlers:
            handlers.remove(handler)

    async def publish(self, event: Event) -> None:
        async with self._lock:
            self._history.append(event)

        handlers = list(self._handlers.get(event.type, [])) + list(self._wildcard_handlers)
        if not handlers:
            return

        results = await asyncio.gather(
            *[h(event) for h in handlers], return_exceptions=True
        )
        for result, handler in zip(results, handlers):
            if isinstance(result, Exception):
                logger.warning(
                    "Handler %s raised exception for event %s: %s",
                    handler.__qualname__,
                    event.type,
                    result,
                )

    def history(self, event_type: EventType | None = None) -> list[Event]:
        if event_type is None:
            return list(self._history)
        return [e for e in self._history if e.type == event_type]

    def clear_history(self) -> None:
        self._history.clear()
