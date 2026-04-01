"""Cross-project pattern finder — identifies recurring patterns and anti-patterns."""

from __future__ import annotations

from typing import Any

from ..core.agent import AgentResult, BaseAgent
from ..core.state import PatternResult


class PatternAnalystAgent(BaseAgent):
    """
    Identifies patterns, anti-patterns, and cross-project insights
    from the accumulated scan and research data.
    """

    name = "pattern_analyst"

    @property
    def system_prompt(self) -> str:
        return (
            "You are a systems thinker who specializes in identifying recurring patterns across "
            "software projects, codebases, and engineering teams. "
            "You distinguish signal from noise, find non-obvious connections, and surface "
            "anti-patterns that most engineers miss because they're too close to the work. "
            "Your recommendations are specific and actionable, not generic best-practice platitudes."
        )

    async def run(self, subject: str, **_: Any) -> AgentResult:
        state = await self._state.get()

        # Build context from available data
        context_parts: list[str] = [f"Subject: {subject}"]

        if state.scan:
            langs = ", ".join(
                f"{l}: {c:,}" for l, c in list(state.scan.languages.items())[:5]
            )
            context_parts.append(
                f"Codebase: {state.scan.file_count} files, {state.scan.total_lines:,} lines\n"
                f"Languages: {langs}\n"
                f"Summary: {state.scan.summary[:500]}"
            )

        if state.research:
            context_parts.append(
                f"Research findings:\n" +
                "\n".join(f"• {f}" for f in state.research.findings[:5])
            )

        context = "\n\n".join(context_parts)

        # Pattern detection
        patterns_prompt = f"""{context}

---
Identify 3-5 PATTERNS in this subject area. Patterns are recurring, structural tendencies that appear across multiple projects or contexts.

For each pattern:
PATTERN [N]: <name>
DESCRIPTION: <what it is and why it recurs>
EVIDENCE: <specific examples or data points>
IMPLICATION: <what this means for the subject>"""

        patterns_text = await self._llm([{"role": "user", "content": patterns_prompt}])

        # Anti-pattern detection
        anti_patterns_prompt = f"""{context}

---
Identify 3-5 ANTI-PATTERNS — recurring failure modes that look reasonable at first but cause problems.

For each anti-pattern:
ANTI-PATTERN [N]: <name>
DESCRIPTION: <what it is and why it's seductive>
FAILURE MODE: <how and when it breaks down>
ALTERNATIVE: <what to do instead>"""

        anti_patterns_text = await self._llm([{"role": "user", "content": anti_patterns_prompt}])

        # Recommendations
        recs_prompt = f"""Based on the patterns and anti-patterns identified for: {subject}

Patterns found:
{patterns_text[:800]}

Anti-patterns found:
{anti_patterns_text[:800]}

Generate 5 specific, prioritized recommendations. Each should be:
- Actionable (someone can start on it today)
- Justified (reference a specific pattern or anti-pattern above)
- Scoped (not vague advice like "write more tests")

Format: RECOMMENDATION [N]: <specific action>"""

        recs_text = await self._llm([{"role": "user", "content": recs_prompt}])

        patterns = self._parse_items(patterns_text, "PATTERN")
        anti_patterns = self._parse_items(anti_patterns_text, "ANTI-PATTERN")
        recommendations = self._parse_recs(recs_text)

        result = PatternResult(
            patterns=[{"name": p, "source": "pattern_analyst"} for p in patterns],
            anti_patterns=[{"name": ap, "source": "pattern_analyst"} for ap in anti_patterns],
            recommendations=recommendations,
        )

        await self._state.set_typed("patterns", result)

        return AgentResult(
            agent_name=self.name,
            success=True,
            output=result.model_dump(),
        )

    def _parse_items(self, text: str, prefix: str) -> list[str]:
        items: list[str] = []
        for line in text.split("\n"):
            line = line.strip()
            if line.upper().startswith(prefix) and ":" in line:
                item = line.split(":", 1)[1].strip()
                if item:
                    items.append(item)
        return items

    def _parse_recs(self, text: str) -> list[str]:
        recs: list[str] = []
        for line in text.split("\n"):
            line = line.strip()
            if line.upper().startswith("RECOMMENDATION") and ":" in line:
                rec = line.split(":", 1)[1].strip()
                if rec:
                    recs.append(rec)
        return recs if recs else [text[:300]]
