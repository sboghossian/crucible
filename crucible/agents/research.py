"""Web research agent — synthesizes knowledge about a topic via LLM."""

from __future__ import annotations

from typing import Any

from ..core.agent import AgentResult, BaseAgent
from ..core.state import ResearchResult


class ResearchAgent(BaseAgent):
    """
    Research agent that synthesizes current knowledge about a topic.

    In the MVP, this uses the LLM's training knowledge. In production,
    plug in web search via httpx + search API (Brave, Tavily, etc.).
    """

    name = "research"

    @property
    def system_prompt(self) -> str:
        return (
            "You are a principal research analyst with expertise across software engineering, "
            "AI/ML, product strategy, and open-source ecosystems. "
            "You synthesize complex topics into structured, evidence-based findings. "
            "Cite specific examples, projects, papers, or companies when possible. "
            "Flag uncertainty explicitly — never fabricate specifics."
        )

    async def run(self, query: str, **_: Any) -> AgentResult:
        # Phase 1: Generate structured findings
        findings_prompt = f"""Research topic: {query}

Generate 5-7 specific, concrete findings about this topic.

For each finding:
1. State the finding as a clear, falsifiable claim
2. Provide supporting evidence or examples
3. Rate your confidence: HIGH / MEDIUM / LOW

Format each finding as:
FINDING [N]: <claim>
EVIDENCE: <supporting evidence>
CONFIDENCE: <HIGH|MEDIUM|LOW>"""

        findings_text = await self._llm([{"role": "user", "content": findings_prompt}])

        # Parse findings
        findings = self._parse_findings(findings_text)

        # Phase 2: Synthesize into a coherent narrative
        synthesis_prompt = f"""Research topic: {query}

Raw findings:
{findings_text}

Now synthesize these findings into a coherent 2-3 paragraph analysis that:
1. Identifies the most important insight
2. Highlights tensions or contradictions in the evidence
3. Suggests the most important open question that further research should address"""

        synthesis = await self._llm([{"role": "user", "content": synthesis_prompt}])

        result = ResearchResult(
            query=query,
            findings=findings,
            sources=["LLM knowledge synthesis (MVP — plug in live search for production)"],
            synthesis=synthesis,
        )

        await self._state.set_typed("research", result)

        return AgentResult(
            agent_name=self.name,
            success=True,
            output=result.model_dump(),
        )

    def _parse_findings(self, text: str) -> list[str]:
        """Extract finding statements from the structured response."""
        findings: list[str] = []
        for line in text.split("\n"):
            line = line.strip()
            if line.startswith("FINDING"):
                # Extract the claim portion after the colon
                if ":" in line:
                    claim = line.split(":", 1)[1].strip()
                    if claim:
                        findings.append(claim)
        return findings if findings else [text[:500]]
