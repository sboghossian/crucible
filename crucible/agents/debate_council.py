"""Debate Council agent — wraps the debate subsystem as a first-class agent."""

from __future__ import annotations

from typing import Any

from ..core.agent import AgentResult, BaseAgent
from ..debate.protocol import DebateProtocol
from ..debate.resolver import format_summary, resolve, to_debate_result


class DebateCouncilAgent(BaseAgent):
    """
    The Debate Council — 4 AI personas debate any topic adversarially.

    This agent wraps the debate subsystem and can be used standalone or
    as part of a full orchestrator run. For orchestrated use, prefer
    `Orchestrator.decide()` which handles state and event bus integration.
    """

    name = "debate_council"

    async def run(
        self,
        topic: str,
        context: str = "",
        options: list[str] | None = None,
        verbose: bool = False,
        **_: Any,
    ) -> AgentResult:
        protocol = DebateProtocol(
            client=self._client,
            model=self._config.model,
            max_tokens=self._config.max_tokens,
        )

        transcript = await protocol.run(
            topic=topic,
            context=context,
            options=options or [],
        )

        result = to_debate_result(transcript)
        resolution = resolve(transcript)
        summary = format_summary(resolution, verbose=verbose)

        await self._state.set_typed("debate", result)

        return AgentResult(
            agent_name=self.name,
            success=True,
            output={
                "winner": result.winner,
                "winner_score": result.winner_score,
                "scores": result.scores,
                "decision": result.decision,
                "summary": summary,
                "dissenting_views": result.dissenting_views,
            },
        )
