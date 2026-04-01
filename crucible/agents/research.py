"""Web research agent — synthesizes knowledge about a topic via LLM."""

from __future__ import annotations

from typing import Any

import anthropic

from ..core.agent import AgentConfig, AgentResult, BaseAgent
from ..core.events import EventBus
from ..core.state import ResearchResult, SharedState
from ..search.engine import SearchEngine
from ..search.result import SearchResult


class ResearchAgent(BaseAgent):
    """
    Research agent that synthesizes knowledge about a topic.

    When a ``search_engine`` is provided, the agent first pulls live web
    results and uses them as grounding context for the LLM synthesis.  All
    retrieved URLs are cited in the output.
    """

    name = "research"

    def __init__(
        self,
        client: anthropic.AsyncAnthropic,
        state: SharedState,
        bus: EventBus,
        config: AgentConfig | None = None,
        search_engine: SearchEngine | None = None,
    ) -> None:
        super().__init__(client, state, bus, config)
        self._search_engine = search_engine

    @property
    def system_prompt(self) -> str:
        return (
            "You are a principal research analyst with expertise across software engineering, "
            "AI/ML, product strategy, and open-source ecosystems. "
            "You synthesize complex topics into structured, evidence-based findings. "
            "Cite specific examples, projects, papers, or companies when possible. "
            "Flag uncertainty explicitly — never fabricate specifics."
        )

    async def web_search(self, query: str, max_results: int = 5) -> list[SearchResult]:
        """Perform a live web search and return results. Returns [] if no engine."""
        if self._search_engine is None:
            return []
        return await self._search_engine.search(query, max_results=max_results)

    async def run(self, query: str, **_: Any) -> AgentResult:
        # Phase 0: Live web search (if engine configured)
        search_results = await self.web_search(query)
        search_context = _format_search_context(search_results)

        # Phase 1: Generate structured findings
        findings_prompt = f"""Research topic: {query}
{search_context}
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
{search_context}
Raw findings:
{findings_text}

Now synthesize these findings into a coherent 2-3 paragraph analysis that:
1. Identifies the most important insight
2. Highlights tensions or contradictions in the evidence
3. Suggests the most important open question that further research should address"""

        synthesis = await self._llm([{"role": "user", "content": synthesis_prompt}])

        # Build source list — cite real URLs when available
        if search_results:
            sources = [r.cite() for r in search_results]
        else:
            sources = ["LLM knowledge synthesis (no live search configured)"]

        result = ResearchResult(
            query=query,
            findings=findings,
            sources=sources,
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
                if ":" in line:
                    claim = line.split(":", 1)[1].strip()
                    if claim:
                        findings.append(claim)
        return findings if findings else [text[:500]]


def _format_search_context(results: list[SearchResult]) -> str:
    """Format search results as an LLM-friendly context block."""
    if not results:
        return ""
    lines = [r.to_context_line() for r in results]
    return (
        "\nRecent web search results (use these as grounding evidence):\n"
        + "\n".join(lines)
        + "\n"
    )
