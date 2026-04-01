"""AsyncIterator-based streaming that yields debate events as they happen."""

from __future__ import annotations

import logging
from typing import AsyncIterator

import anthropic

from ..debate.personas import ALL_PERSONAS, Persona
from ..debate.protocol import (
    DebateProtocol,
    DebateTranscript,
    Statement,
)
from .events import (
    ROUND_LABELS,
    ArgumentSubmitted,
    CrossExamination,
    DebateEvent,
    DebateStarted,
    PersonaThinking,
    ScoringComplete,
    ScoringStarted,
    WinnerDeclared,
)

logger = logging.getLogger(__name__)


class DebateStream:
    """
    Streams debate events as they happen, yielding typed DebateEvent objects.

    Each round runs sequentially so events surface naturally in order:
    each persona's thinking → argument → next persona.

    Usage:
        async for event in stream.run(topic):
            handle(event)
    """

    def __init__(
        self,
        client: anthropic.AsyncAnthropic,
        model: str = "claude-opus-4-6",
        max_tokens: int = 1024,
    ) -> None:
        self._client = client
        self._model = model
        self._max_tokens = max_tokens
        self._protocol = DebateProtocol(client=client, model=model, max_tokens=max_tokens)

    async def run(
        self,
        topic: str,
        context: str = "",
        options: list[str] | None = None,
    ) -> AsyncIterator[DebateEvent]:
        """
        Async generator that yields DebateEvent objects as the debate unfolds.

        Usage:
            async for event in stream.run("Should we use microservices?"):
                ...
        """
        options = options or []
        yield DebateStarted(topic=topic, context=context, options=options)

        transcript = DebateTranscript(topic=topic, context=context, options=options)
        options_text = "\n".join(f"- {o}" for o in options) if options else "Open-ended"

        # Round 1: Opening statements
        opening_statements: list[Statement] = []
        opening_prompt = self._protocol._build_opening_prompt(topic, context, options)
        async for event in self._run_round_sequentially(ALL_PERSONAS, opening_prompt, round_num=1):
            yield event
            if isinstance(event, ArgumentSubmitted):
                stmt = Statement(persona_name=event.persona_name, round=1, content=event.content)
                opening_statements.append(stmt)
                transcript.statements.append(stmt)

        # Round 2: Cross-examination
        cross_statements: list[Statement] = []
        transcript_text_r1 = DebateProtocol._format_statements(opening_statements)
        cross_prompt = (
            f"DEBATE TOPIC: {topic}\n\n"
            + (f"CONTEXT: {context}\n\n" if context else "")
            + f"OPTIONS UNDER CONSIDERATION:\n{options_text}\n\n"
            + f"ROUND 1 OPENING STATEMENTS FROM ALL PARTICIPANTS:\n{transcript_text_r1}\n\n"
            + "---\nROUND 2 — CROSS-EXAMINATION\n\n"
            + "You have read all opening statements. Now challenge the other participants directly.\n\n"
            + "Requirements:\n"
            + "1. Pick the 2 WEAKEST arguments from other personas (name them explicitly).\n"
            + "2. Explain precisely why each argument fails or is incomplete.\n"
            + "3. Reinforce your own position in light of what you have read.\n"
            + "4. Be direct and specific — no diplomatic hedging.\n\n"
            + 'Start with: "Cross-examination:"'
        )
        async for event in self._run_round_sequentially(ALL_PERSONAS, cross_prompt, round_num=2):
            yield event
            if isinstance(event, CrossExamination):
                stmt = Statement(
                    persona_name=event.persona_name,
                    round=2,
                    content=event.content,
                    targets=event.targets,
                )
                cross_statements.append(stmt)
                transcript.statements.append(stmt)

        # Round 3: Closing arguments
        closing_statements: list[Statement] = []
        transcript_text_r1r2 = DebateProtocol._format_statements(
            opening_statements + cross_statements
        )
        closing_prompt = (
            f"DEBATE TOPIC: {topic}\n\n"
            + (f"CONTEXT: {context}\n\n" if context else "")
            + f"OPTIONS UNDER CONSIDERATION:\n{options_text}\n\n"
            + f"FULL DEBATE TRANSCRIPT (Rounds 1 and 2):\n{transcript_text_r1r2}\n\n"
            + "---\nROUND 3 — CLOSING ARGUMENT\n\n"
            + "You have heard all arguments and challenges. This is your final statement.\n\n"
            + "Requirements:\n"
            + "1. State your FINAL RECOMMENDATION clearly in the first sentence.\n"
            + "2. Acknowledge the strongest point made against your position and explain why it doesn't change your conclusion.\n"
            + "3. Identify the one argument from any persona (including yourself) that you found most compelling.\n"
            + "4. If you have updated your position, say so explicitly — intellectual honesty is respected.\n\n"
            + 'Start with: "Closing argument:"'
        )
        async for event in self._run_round_sequentially(ALL_PERSONAS, closing_prompt, round_num=3):
            yield event
            if isinstance(event, ArgumentSubmitted):
                stmt = Statement(persona_name=event.persona_name, round=3, content=event.content)
                closing_statements.append(stmt)
                transcript.statements.append(stmt)

        # Scoring
        yield ScoringStarted()
        await self._protocol._score_transcript(transcript)
        yield ScoringComplete(scores=dict(transcript.scores))

        yield WinnerDeclared(
            winner=transcript.winner,
            winner_score=transcript.winner_score,
            decision=transcript.decision,
            dissenting_views=list(transcript.dissenting_views),
        )

    async def _run_round_sequentially(
        self,
        personas: list[Persona],
        prompt: str,
        round_num: int,
    ) -> AsyncIterator[DebateEvent]:
        """Yield PersonaThinking then the statement event for each persona, one at a time."""
        round_label = ROUND_LABELS.get(round_num, f"Round {round_num}")
        for persona in personas:
            yield PersonaThinking(
                persona_name=persona.name,
                round=round_num,
                round_label=round_label,
            )
            content = await self._get_statement_content(persona, prompt, round_num)

            targets: list[str] = []
            if round_num == 2:
                for p in ALL_PERSONAS:
                    if p.name != persona.name and p.role.lower() in content.lower():
                        targets.append(p.name)

            if round_num == 2:
                yield CrossExamination(
                    persona_name=persona.name,
                    content=content,
                    targets=targets,
                )
            else:
                yield ArgumentSubmitted(
                    persona_name=persona.name,
                    round=round_num,
                    round_label=round_label,
                    content=content,
                    targets=targets,
                )

    async def _get_statement_content(
        self, persona: Persona, prompt: str, round_num: int
    ) -> str:
        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                system=persona.system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text  # type: ignore[union-attr]
        except Exception as exc:
            logger.error("Persona %s failed in round %d: %s", persona.name, round_num, exc)
            return f"[Statement unavailable: {exc}]"
