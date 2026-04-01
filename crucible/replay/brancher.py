"""Forks a recorded debate from a specific round with new personas or a new prompt."""

from __future__ import annotations

import dataclasses
import json
import time
import uuid
from typing import AsyncIterator

import anthropic

from ..debate.personas import ALL_PERSONAS, PERSONA_BY_NAME, Persona
from ..debate.protocol import DebateProtocol, DebateTranscript, Statement
from ..memory.sqlite_store import SQLiteMemoryStore
from ..streaming.events import (
    ROUND_LABELS,
    ArgumentSubmitted,
    CrossExamination,
    DebateEvent,
    PersonaThinking,
    ScoringComplete,
    ScoringStarted,
    WinnerDeclared,
)
from ._serde import event_from_row, event_round, event_to_json

import logging

logger = logging.getLogger(__name__)


class DebateBrancher:
    """
    Forks a recorded debate at a given round, optionally with new personas or prompt.

    Usage::

        brancher = DebateBrancher(store)
        branch_id = brancher.branch(debate_id, round_number=2, new_personas=["pragmatist"])
        async for event in brancher.run_branch(branch_id, client, model):
            renderer.render(event)
    """

    def __init__(self, store: SQLiteMemoryStore) -> None:
        self._store = store

    def branch(
        self,
        debate_id: str,
        round_number: int,
        new_personas: list[str] | None = None,
        new_prompt: str | None = None,
    ) -> str:
        """
        Create a branch of debate_id forked after round_number.

        The branch inherits all events up to and including round_number.
        Returns the new branch_id.
        """
        session = self._store.get_debate_session(debate_id)
        if session is None:
            raise ValueError(f"Debate session not found: {debate_id!r}")

        branch_id = str(uuid.uuid4())
        branch_personas = new_personas if new_personas is not None else session["personas"]
        branch_topic = new_prompt or session["topic"]

        self._store.save_debate_session(
            session_id=branch_id,
            topic=branch_topic,
            context=session["context"],
            options=session["options"],
            personas=branch_personas,
            parent_debate_id=debate_id,
            branch_round=round_number,
            new_prompt=new_prompt,
        )

        # Copy inherited events (rounds 0..round_number) into the branch
        inherited = self._store.get_debate_events(debate_id, max_round=round_number)
        for i, row in enumerate(inherited):
            self._store.save_debate_event(
                debate_id=branch_id,
                seq=i,
                round_number=row["round_number"],
                persona=row["persona"],
                event_kind=row["event_kind"],
                event_json=row["event_json"],
                elapsed_ms=row["elapsed_ms"],
            )

        return branch_id

    async def run_branch(
        self,
        branch_id: str,
        client: anthropic.AsyncAnthropic,
        model: str = "claude-opus-4-6",
        max_tokens: int = 1024,
    ) -> AsyncIterator[DebateEvent]:
        """
        Run the continuation of a branched debate.

        Re-emits inherited events, then runs new rounds with (optionally) new personas.
        New events are recorded to SQLite as they are produced.
        """
        session = self._store.get_debate_session(branch_id)
        if session is None:
            raise ValueError(f"Branch session not found: {branch_id!r}")

        branch_round: int = session["branch_round"] or 0
        topic: str = session["topic"]
        context: str = session["context"]
        options: list[str] = session["options"]

        # Resolve personas
        persona_names: list[str] = session["personas"]
        if persona_names:
            personas: list[Persona] = [
                PERSONA_BY_NAME[n] for n in persona_names if n in PERSONA_BY_NAME
            ]
        else:
            personas = list(ALL_PERSONAS)
        if not personas:
            personas = list(ALL_PERSONAS)

        # Fetch inherited events already stored in the branch
        inherited_rows = self._store.get_debate_events(branch_id, max_round=branch_round)

        # Re-emit inherited events
        for row in inherited_rows:
            yield event_from_row(row)

        # Reconstruct Statement objects from inherited events for prompt building
        opening_statements: list[Statement] = []
        cross_statements: list[Statement] = []
        for row in inherited_rows:
            kind = row["event_kind"]
            d: dict = json.loads(row["event_json"])
            if kind == "argument_submitted" and d.get("round") == 1:
                opening_statements.append(
                    Statement(persona_name=d["persona_name"], round=1, content=d["content"])
                )
            elif kind == "cross_examination":
                cross_statements.append(
                    Statement(
                        persona_name=d["persona_name"],
                        round=2,
                        content=d["content"],
                        targets=d.get("targets", []),
                    )
                )

        # Run remaining rounds via _BranchedStream and record new events
        protocol = DebateProtocol(
            client=client, model=model, max_tokens=max_tokens, personas=personas
        )
        new_stream = _BranchedStream(
            protocol=protocol,
            topic=topic,
            context=context,
            options=options,
            opening_statements=opening_statements,
            cross_statements=cross_statements,
            branch_round=branch_round,
        )

        start = time.monotonic()
        seq = len(inherited_rows)
        try:
            async for event in new_stream.run():
                elapsed_ms = int((time.monotonic() - start) * 1000)
                self._store.save_debate_event(
                    debate_id=branch_id,
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
            self._store.mark_debate_session_complete(branch_id, seq)

    def get_branch_tree(self, root_debate_id: str) -> dict[str, list[dict]]:
        """Return mapping of debate_id -> list of direct child branches."""
        return self._store.get_branch_tree(root_debate_id)


class _BranchedStream:
    """
    Runs a debate starting after branch_round, using inherited statements as context.

    Runs only the rounds that were NOT inherited (branch_round+1 through 3).
    """

    def __init__(
        self,
        protocol: DebateProtocol,
        topic: str,
        context: str,
        options: list[str],
        opening_statements: list[Statement],
        cross_statements: list[Statement],
        branch_round: int,
    ) -> None:
        self._protocol = protocol
        self._topic = topic
        self._context = context
        self._options = options
        self._opening_stmts = opening_statements
        self._cross_stmts = cross_statements
        self._branch_round = branch_round

    async def run(self) -> AsyncIterator[DebateEvent]:
        options_text = (
            "\n".join(f"- {o}" for o in self._options) if self._options else "Open-ended"
        )
        opening_stmts = list(self._opening_stmts)
        cross_stmts = list(self._cross_stmts)
        closing_stmts: list[Statement] = []

        # Round 1 — only if not inherited
        if self._branch_round < 1:
            opening_prompt = self._protocol._build_opening_prompt(
                self._topic, self._context, self._options
            )
            async for event in self._run_round(opening_prompt, 1, False, opening_stmts):
                yield event

        # Round 2 — only if not inherited
        if self._branch_round < 2:
            r1_text = DebateProtocol._format_statements(opening_stmts)
            cross_prompt = (
                f"DEBATE TOPIC: {self._topic}\n\n"
                + (f"CONTEXT: {self._context}\n\n" if self._context else "")
                + f"OPTIONS UNDER CONSIDERATION:\n{options_text}\n\n"
                + f"ROUND 1 OPENING STATEMENTS FROM ALL PARTICIPANTS:\n{r1_text}\n\n"
                + "---\nROUND 2 — CROSS-EXAMINATION\n\n"
                + "You have read all opening statements. Now challenge the other participants directly.\n\n"
                + "Requirements:\n"
                + "1. Pick the 2 WEAKEST arguments from other personas (name them explicitly).\n"
                + "2. Explain precisely why each argument fails or is incomplete.\n"
                + "3. Reinforce your own position in light of what you have read.\n"
                + "4. Be direct and specific — no diplomatic hedging.\n\n"
                + 'Start with: "Cross-examination:"'
            )
            async for event in self._run_round(cross_prompt, 2, True, cross_stmts):
                yield event

        # Round 3 — always run in the branch
        r1r2_text = DebateProtocol._format_statements(opening_stmts + cross_stmts)
        closing_prompt = (
            f"DEBATE TOPIC: {self._topic}\n\n"
            + (f"CONTEXT: {self._context}\n\n" if self._context else "")
            + f"OPTIONS UNDER CONSIDERATION:\n{options_text}\n\n"
            + f"FULL DEBATE TRANSCRIPT (Rounds 1 and 2):\n{r1r2_text}\n\n"
            + "---\nROUND 3 — CLOSING ARGUMENT\n\n"
            + "You have heard all arguments and challenges. This is your final statement.\n\n"
            + "Requirements:\n"
            + "1. State your FINAL RECOMMENDATION clearly in the first sentence.\n"
            + "2. Acknowledge the strongest point made against your position and explain why it doesn't change your conclusion.\n"
            + "3. Identify the one argument from any persona (including yourself) that you found most compelling.\n"
            + "4. If you have updated your position, say so explicitly — intellectual honesty is respected.\n\n"
            + 'Start with: "Closing argument:"'
        )
        async for event in self._run_round(closing_prompt, 3, False, closing_stmts):
            yield event

        # Scoring
        yield ScoringStarted()
        transcript = DebateTranscript(
            topic=self._topic,
            context=self._context,
            options=self._options,
            statements=opening_stmts + cross_stmts + closing_stmts,
        )
        await self._protocol._score_transcript(transcript)
        yield ScoringComplete(scores=dict(transcript.scores))
        yield WinnerDeclared(
            winner=transcript.winner,
            winner_score=transcript.winner_score,
            decision=transcript.decision,
            dissenting_views=list(transcript.dissenting_views),
        )

    async def _run_round(
        self,
        prompt: str,
        round_num: int,
        is_cross: bool,
        stmts_out: list[Statement],
    ) -> AsyncIterator[DebateEvent]:
        """Yield events for one round, appending Statement objects to stmts_out."""
        round_label = ROUND_LABELS.get(round_num, f"Round {round_num}")
        personas = self._protocol._personas
        for persona in personas:
            yield PersonaThinking(
                persona_name=persona.name,
                round=round_num,
                round_label=round_label,
            )
            content = await self._get_content(persona, prompt, round_num)
            targets: list[str] = []
            if is_cross:
                for p in personas:
                    if p.name != persona.name and p.role.lower() in content.lower():
                        targets.append(p.name)
            if is_cross:
                stmts_out.append(
                    Statement(
                        persona_name=persona.name,
                        round=2,
                        content=content,
                        targets=targets,
                    )
                )
                yield CrossExamination(
                    persona_name=persona.name,
                    content=content,
                    targets=targets,
                )
            else:
                stmts_out.append(
                    Statement(persona_name=persona.name, round=round_num, content=content)
                )
                yield ArgumentSubmitted(
                    persona_name=persona.name,
                    round=round_num,
                    round_label=round_label,
                    content=content,
                    targets=targets,
                )

    async def _get_content(self, persona: Persona, prompt: str, round_num: int) -> str:
        try:
            response = await self._protocol._client.messages.create(
                model=self._protocol._model,
                max_tokens=self._protocol._max_tokens,
                system=persona.system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text  # type: ignore[union-attr]
        except Exception as exc:
            logger.error("Persona %s failed in round %d: %s", persona.name, round_num, exc)
            return f"[Statement unavailable: {exc}]"
