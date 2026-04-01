"""Meta-agent that watches all other agents and learns from their outputs."""

from __future__ import annotations

import asyncio
import os
from typing import Any

from ..core.agent import AgentResult, BaseAgent
from ..core.events import Event, EventType
from ..core.state import LearningRecord
from ..memory.sqlite_store import SQLiteMemoryStore


class LearningAgent(BaseAgent):
    """
    Observes all agent events via the event bus and distills meta-patterns.

    This agent runs passively throughout a research session, accumulating
    observations. It is activated as an event listener (via on_event) and
    also has an active run() method that synthesizes all observations at
    the end of a session.
    """

    name = "learning"

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        db_path = kwargs.pop("db_path", ".crucible_memory.db")
        super().__init__(*args, **kwargs)
        self._observations: list[dict[str, Any]] = []
        self._lock = asyncio.Lock()
        self._memory = SQLiteMemoryStore(db_path=db_path)

    async def on_event(self, event: Event) -> None:
        """Passive listener — called for every event on the bus."""
        interesting_types = {
            EventType.AGENT_OUTPUT,
            EventType.AGENT_FAILED,
            EventType.DEBATE_COMPLETED,
        }
        if event.type not in interesting_types:
            return

        observation = {
            "event_type": event.type.value,
            "source": event.source,
            "payload_summary": str(event.payload)[:300],
            "timestamp": event.timestamp.isoformat(),
        }

        async with self._lock:
            self._observations.append(observation)

        # For failures, record immediately
        if event.type == EventType.AGENT_FAILED:
            error_msg = event.payload.get("error", "unknown error")
            record = LearningRecord(
                agent_name=event.source,
                observation=f"Agent failed: {error_msg}",
                pattern="failure",
            )
            await self._state.append_learning(record)
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._memory.save_learning(
                    agent_name=event.source,
                    pattern="failure",
                    insight=f"Agent failed: {error_msg}",
                ),
            )

        # For debate completions, record the decision
        if event.type == EventType.DEBATE_COMPLETED:
            winner = event.payload.get("winner", "unknown")
            topic = event.payload.get("topic", "unknown")
            record = LearningRecord(
                agent_name="debate_council",
                observation=f"Debate on '{topic}' resolved to: {winner}",
                pattern="decision",
            )
            await self._state.append_learning(record)
            await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self._memory.save_learning(
                    agent_name="debate_council",
                    pattern="decision",
                    insight=f"Debate on '{topic}' resolved to: {winner}",
                ),
            )

    async def run(self, **_: Any) -> AgentResult:
        """
        Synthesize all observations from the session into meta-patterns.
        Call this at the end of a run to get the learning summary.
        """
        async with self._lock:
            observations = list(self._observations)

        if not observations:
            return AgentResult(
                agent_name=self.name,
                success=True,
                output={"meta_patterns": [], "synthesis": "No observations collected."},
            )

        obs_text = "\n".join(
            f"[{o['source']} / {o['event_type']}]: {o['payload_summary']}"
            for o in observations[:30]  # cap context
        )

        # Pull relevant historical learnings to enrich the synthesis
        loop = asyncio.get_event_loop()
        historical = await loop.run_in_executor(
            None,
            lambda: self._memory.get_learnings(limit=20),
        )
        history_text = ""
        if historical:
            history_lines = "\n".join(
                f"- [{h['agent_name']} / {h['pattern']}]: {h['insight']}"
                for h in historical[:10]
            )
            history_text = f"\n\nHistorical learnings from prior sessions:\n{history_lines}"

        prompt = f"""You are a meta-learning system that watches AI research agents work and distills transferable insights.

Session observations:
{obs_text}{history_text}

Analyze these observations and identify:
1. META-PATTERNS: What recurring behaviors, successes, or failure modes appear across agents?
2. CALIBRATION INSIGHTS: Where do agents seem overconfident or underconfident?
3. COLLABORATION INSIGHTS: How did agents build on each other's work (or miss opportunities)?
4. IMPROVEMENT SUGGESTIONS: What should change in the next research session?

Be specific. Reference actual observations, not generic advice."""

        synthesis = await self._llm([{"role": "user", "content": prompt}])

        # Extract meta-patterns
        patterns = [
            line.strip()
            for line in synthesis.split("\n")
            if line.strip().startswith("META-PATTERN") or line.strip().startswith("•")
        ][:10]

        record = LearningRecord(
            agent_name=self.name,
            observation=f"Session synthesis: {len(observations)} events observed",
            pattern="meta_synthesis",
        )
        await self._state.append_learning(record)

        await asyncio.get_event_loop().run_in_executor(
            None,
            lambda: self._memory.save_learning(
                agent_name=self.name,
                pattern="meta_synthesis",
                insight=synthesis[:500],
            ),
        )

        return AgentResult(
            agent_name=self.name,
            success=True,
            output={
                "observations_count": len(observations),
                "meta_patterns": patterns,
                "synthesis": synthesis,
            },
        )
