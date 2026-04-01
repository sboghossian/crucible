"""Base agent class for all Crucible agents."""

from __future__ import annotations

import asyncio
import uuid
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any

import anthropic
from pydantic import BaseModel

from .events import Event, EventBus, EventType
from .state import SharedState

import logging

logger = logging.getLogger(__name__)


class AgentConfig(BaseModel):
    model: str = "claude-opus-4-6"
    max_tokens: int = 4096
    temperature: float = 1.0
    timeout: float = 120.0


class AgentResult(BaseModel):
    agent_name: str
    success: bool
    output: Any
    error: str | None = None
    duration_seconds: float = 0.0
    tokens_used: int = 0


class BaseAgent(ABC):
    """
    Base class for all Crucible agents.

    Subclasses implement `run()` and optionally override `system_prompt`.
    The base class handles lifecycle events, error handling, and LLM access.
    """

    name: str = "base_agent"

    def __init__(
        self,
        client: anthropic.AsyncAnthropic,
        state: SharedState,
        bus: EventBus,
        config: AgentConfig | None = None,
    ) -> None:
        self._client = client
        self._state = state
        self._bus = bus
        self._config = config or AgentConfig()

    @property
    def system_prompt(self) -> str:
        return f"You are {self.name}, a specialized AI research agent. Be precise, analytical, and evidence-based."

    @abstractmethod
    async def run(self, **kwargs: Any) -> AgentResult:
        """Execute the agent's primary task. Must be implemented by subclasses."""
        ...

    async def execute(self, **kwargs: Any) -> AgentResult:
        """Wrap run() with lifecycle events and error handling."""
        start = datetime.utcnow()
        run_state = await self._state.get()
        run_id = run_state.run_id

        await self._bus.publish(Event(
            type=EventType.AGENT_STARTED,
            source=self.name,
            payload={"kwargs": {k: str(v)[:200] for k, v in kwargs.items()}},
            run_id=run_id,
        ))

        try:
            result = await asyncio.wait_for(
                self.run(**kwargs), timeout=self._config.timeout
            )
            result.duration_seconds = (datetime.utcnow() - start).total_seconds()

            await self._bus.publish(Event(
                type=EventType.AGENT_COMPLETED,
                source=self.name,
                payload={"duration": result.duration_seconds, "success": result.success},
                run_id=run_id,
            ))
            await self._bus.publish(Event(
                type=EventType.AGENT_OUTPUT,
                source=self.name,
                payload={"output": result.output if isinstance(result.output, dict) else str(result.output)[:500]},
                run_id=run_id,
            ))
            return result

        except asyncio.TimeoutError:
            error = f"Agent {self.name} timed out after {self._config.timeout}s"
            logger.error(error)
            await self._state.append_error(self.name, error)
            await self._bus.publish(Event(
                type=EventType.AGENT_FAILED,
                source=self.name,
                payload={"error": error},
                run_id=run_id,
            ))
            return AgentResult(
                agent_name=self.name,
                success=False,
                output=None,
                error=error,
                duration_seconds=(datetime.utcnow() - start).total_seconds(),
            )
        except Exception as exc:
            error = str(exc)
            logger.exception("Agent %s failed: %s", self.name, error)
            await self._state.append_error(self.name, error)
            await self._bus.publish(Event(
                type=EventType.AGENT_FAILED,
                source=self.name,
                payload={"error": error},
                run_id=run_id,
            ))
            return AgentResult(
                agent_name=self.name,
                success=False,
                output=None,
                error=error,
                duration_seconds=(datetime.utcnow() - start).total_seconds(),
            )

    async def _llm(
        self,
        messages: list[dict[str, str]],
        system: str | None = None,
        max_tokens: int | None = None,
    ) -> str:
        """Call the LLM and return the text response."""
        response = await self._client.messages.create(
            model=self._config.model,
            max_tokens=max_tokens or self._config.max_tokens,
            system=system or self.system_prompt,
            messages=messages,  # type: ignore[arg-type]
        )
        return response.content[0].text  # type: ignore[union-attr]
