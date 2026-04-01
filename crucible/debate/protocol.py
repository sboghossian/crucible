"""Adversarial debate protocol: 3 rounds with cross-examination and scoring."""

from __future__ import annotations

import asyncio
from dataclasses import dataclass, field
from typing import Any

import anthropic

from .personas import ALL_PERSONAS, Persona

import logging

logger = logging.getLogger(__name__)


@dataclass
class Statement:
    persona_name: str
    round: int  # 1=opening, 2=cross-exam, 3=closing
    content: str
    targets: list[str] = field(default_factory=list)  # personas being challenged


@dataclass
class DebateTranscript:
    topic: str
    context: str
    options: list[str]
    statements: list[Statement] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)
    winner: str = ""
    winner_score: float = 0.0
    decision: str = ""
    dissenting_views: list[str] = field(default_factory=list)


SCORING_CRITERIA = """
Score this statement on a scale of 0-10 for each criterion:

1. **Evidence Quality** (0-10): Are claims backed by concrete evidence, data, or specific examples? Or vague assertions?
2. **Logical Consistency** (0-10): Is the argument internally consistent? Do conclusions follow from premises?
3. **Practical Feasibility** (0-10): Is the proposed path actually implementable with real-world constraints?
4. **Novelty** (0-10): Does the argument surface non-obvious insights or reframe the problem usefully?

Respond with ONLY a JSON object, no other text:
{"evidence_quality": X, "logical_consistency": X, "practical_feasibility": X, "novelty": X}
"""


class DebateProtocol:
    """
    Runs a 3-round adversarial debate between the 4 personas.

    Round 1 - Opening Statements: Each persona presents their position independently.
    Round 2 - Cross-Examination: Each persona challenges the others' weakest points.
    Round 3 - Closing Arguments: Each persona refines their position in light of the debate.
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

    async def run(
        self,
        topic: str,
        context: str = "",
        options: list[str] | None = None,
    ) -> DebateTranscript:
        options = options or []
        transcript = DebateTranscript(topic=topic, context=context, options=options)

        logger.info("Debate starting: %s", topic)

        # Round 1: Opening statements (parallel)
        opening_statements = await self._round_opening(topic, context, options)
        transcript.statements.extend(opening_statements)
        logger.info("Round 1 complete: %d opening statements", len(opening_statements))

        # Round 2: Cross-examination (each persona reads all openings, then challenges)
        cross_statements = await self._round_cross_examination(
            topic, context, options, opening_statements
        )
        transcript.statements.extend(cross_statements)
        logger.info("Round 2 complete: %d cross-examination statements", len(cross_statements))

        # Round 3: Closing arguments (each persona has seen all statements)
        all_so_far = opening_statements + cross_statements
        closing_statements = await self._round_closing(
            topic, context, options, all_so_far
        )
        transcript.statements.extend(closing_statements)
        logger.info("Round 3 complete: %d closing statements", len(closing_statements))

        # Score all statements and compute winner
        await self._score_transcript(transcript)

        return transcript

    async def _round_opening(
        self, topic: str, context: str, options: list[str]
    ) -> list[Statement]:
        prompt = self._build_opening_prompt(topic, context, options)
        tasks = [
            self._get_statement(persona, prompt, round_num=1)
            for persona in ALL_PERSONAS
        ]
        return list(await asyncio.gather(*tasks))

    async def _round_cross_examination(
        self,
        topic: str,
        context: str,
        options: list[str],
        prior_statements: list[Statement],
    ) -> list[Statement]:
        transcript_text = self._format_statements(prior_statements)
        tasks = [
            self._get_cross_examination(persona, topic, context, options, transcript_text)
            for persona in ALL_PERSONAS
        ]
        return list(await asyncio.gather(*tasks))

    async def _round_closing(
        self,
        topic: str,
        context: str,
        options: list[str],
        prior_statements: list[Statement],
    ) -> list[Statement]:
        transcript_text = self._format_statements(prior_statements)
        tasks = [
            self._get_closing(persona, topic, context, options, transcript_text)
            for persona in ALL_PERSONAS
        ]
        return list(await asyncio.gather(*tasks))

    async def _get_statement(
        self, persona: Persona, prompt: str, round_num: int
    ) -> Statement:
        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=self._max_tokens,
                system=persona.system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )
            content = response.content[0].text  # type: ignore[union-attr]
        except Exception as exc:
            logger.error("Persona %s failed in round %d: %s", persona.name, round_num, exc)
            content = f"[Statement unavailable: {exc}]"
        return Statement(persona_name=persona.name, round=round_num, content=content)

    async def _get_cross_examination(
        self,
        persona: Persona,
        topic: str,
        context: str,
        options: list[str],
        transcript_text: str,
    ) -> Statement:
        options_text = "\n".join(f"- {o}" for o in options) if options else "Open-ended"
        prompt = f"""DEBATE TOPIC: {topic}

{f"CONTEXT: {context}" if context else ""}

OPTIONS UNDER CONSIDERATION:
{options_text}

ROUND 1 OPENING STATEMENTS FROM ALL PARTICIPANTS:
{transcript_text}

---
ROUND 2 — CROSS-EXAMINATION

You have read all opening statements. Now challenge the other participants directly.

Requirements:
1. Pick the 2 WEAKEST arguments from other personas (name them explicitly).
2. Explain precisely why each argument fails or is incomplete.
3. Reinforce your own position in light of what you have read.
4. Be direct and specific — no diplomatic hedging.

Start with: "Cross-examination:"
"""
        stmt = await self._get_statement(persona, prompt, round_num=2)
        # Parse which personas were challenged
        for p in ALL_PERSONAS:
            if p.name != persona.name and p.role.lower() in stmt.content.lower():
                stmt.targets.append(p.name)
        return stmt

    async def _get_closing(
        self,
        persona: Persona,
        topic: str,
        context: str,
        options: list[str],
        transcript_text: str,
    ) -> Statement:
        options_text = "\n".join(f"- {o}" for o in options) if options else "Open-ended"
        prompt = f"""DEBATE TOPIC: {topic}

{f"CONTEXT: {context}" if context else ""}

OPTIONS UNDER CONSIDERATION:
{options_text}

FULL DEBATE TRANSCRIPT (Rounds 1 and 2):
{transcript_text}

---
ROUND 3 — CLOSING ARGUMENT

You have heard all arguments and challenges. This is your final statement.

Requirements:
1. State your FINAL RECOMMENDATION clearly in the first sentence.
2. Acknowledge the strongest point made against your position and explain why it doesn't change your conclusion.
3. Identify the one argument from any persona (including yourself) that you found most compelling.
4. If you have updated your position, say so explicitly — intellectual honesty is respected.

Start with: "Closing argument:"
"""
        return await self._get_statement(persona, prompt, round_num=3)

    async def _score_transcript(self, transcript: DebateTranscript) -> None:
        """Score each persona's closing argument and compute the winner."""
        closing_statements = [s for s in transcript.statements if s.round == 3]

        score_tasks = [
            self._score_statement(stmt, ALL_PERSONAS[i])
            for i, stmt in enumerate(closing_statements)
        ]
        raw_scores = await asyncio.gather(*score_tasks, return_exceptions=True)

        persona_scores: dict[str, float] = {}
        for stmt, scores_result in zip(closing_statements, raw_scores):
            if isinstance(scores_result, Exception) or not isinstance(scores_result, dict):
                persona_scores[stmt.persona_name] = 5.0  # neutral fallback
                continue

            from .personas import PERSONA_BY_NAME
            persona = PERSONA_BY_NAME.get(stmt.persona_name)
            if persona is None:
                persona_scores[stmt.persona_name] = 5.0
                continue

            # Weighted score based on this persona's own weight profile
            # (We use the EVALUATOR's weights, which creates interesting cross-persona dynamics)
            weighted = sum(
                persona.scoring_weight.get(k, 0.25) * v
                for k, v in scores_result.items()
            )
            persona_scores[stmt.persona_name] = round(weighted, 2)

        transcript.scores = persona_scores

        if persona_scores:
            winner = max(persona_scores, key=persona_scores.__getitem__)
            transcript.winner = winner
            transcript.winner_score = persona_scores[winner]

        # Build final decision from winner's closing
        winner_closing = next(
            (s for s in closing_statements if s.persona_name == transcript.winner), None
        )
        if winner_closing:
            transcript.decision = (
                f"[{transcript.winner.title()} wins with score {transcript.winner_score:.1f}/10]\n\n"
                + winner_closing.content
            )

        # Capture dissenting views from non-winners
        for stmt in closing_statements:
            if stmt.persona_name != transcript.winner:
                first_line = stmt.content.split("\n")[0][:200]
                transcript.dissenting_views.append(
                    f"{stmt.persona_name}: {first_line}"
                )

    async def _score_statement(
        self, statement: Statement, evaluating_persona: Persona
    ) -> dict[str, float]:
        """Score a statement using the evaluating persona's system prompt."""
        import json
        prompt = f"""Statement to evaluate:

---
{statement.content}
---

{SCORING_CRITERIA}"""
        try:
            response = await self._client.messages.create(
                model=self._model,
                max_tokens=200,
                system=evaluating_persona.system_prompt,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text  # type: ignore[union-attr]
            # Extract JSON from the response
            import re
            match = re.search(r'\{[^}]+\}', text, re.DOTALL)
            if match:
                raw = json.loads(match.group())
                return {k: float(v) for k, v in raw.items()}
        except Exception as exc:
            logger.warning("Scoring failed for %s: %s", statement.persona_name, exc)
        return {"evidence_quality": 5.0, "logical_consistency": 5.0,
                "practical_feasibility": 5.0, "novelty": 5.0}

    def _build_opening_prompt(self, topic: str, context: str, options: list[str]) -> str:
        options_text = "\n".join(f"- {o}" for o in options) if options else "Open-ended"
        return f"""DEBATE TOPIC: {topic}

{f"CONTEXT: {context}" if context else ""}

OPTIONS UNDER CONSIDERATION:
{options_text}

---
ROUND 1 — OPENING STATEMENT

Present your position on this topic from your unique perspective.

Requirements:
1. State your recommendation clearly upfront.
2. Give 3 specific, concrete reasons supporting your position.
3. Identify the strongest counterargument against your view and preemptively address it.
4. Be direct. No filler. No hedging.

Start with: "Opening statement:"
"""

    @staticmethod
    def _format_statements(statements: list[Statement]) -> str:
        lines: list[str] = []
        round_labels = {1: "OPENING", 2: "CROSS-EXAMINATION", 3: "CLOSING"}
        for stmt in statements:
            label = round_labels.get(stmt.round, f"ROUND {stmt.round}")
            lines.append(f"[{stmt.persona_name.upper()} — {label}]\n{stmt.content}\n")
        return "\n---\n".join(lines)
