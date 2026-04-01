"""
Example custom plugin: SentimentAnalyzerAgent

Demonstrates the @agent_plugin decorator API.

Usage:
    crucible --plugins-dir examples/custom_plugin research "AI trends"
"""

from __future__ import annotations

from crucible.plugins import agent_plugin
from crucible.core.agent import BaseAgent, AgentResult


@agent_plugin(
    name="sentiment_analyzer",
    description="Analyzes the sentiment and tone of research findings",
    version="1.0.0",
    author="Steph",
)
class SentimentAnalyzerAgent(BaseAgent):
    """Custom agent that scores the sentiment of any text in shared state."""

    name = "sentiment_analyzer"

    async def run(self, **kwargs: object) -> AgentResult:
        subject = kwargs.get("subject", "")

        state = await self._state.get()
        research_text = ""
        if state.research:
            research_text = state.research.synthesis or ""

        if not research_text:
            return AgentResult(
                agent_name=self.name,
                success=True,
                output={"sentiment": "neutral", "score": 0.5, "note": "No research text found"},
            )

        prompt = (
            f"Analyze the sentiment of the following research on '{subject}'.\n\n"
            f"{research_text[:2000]}\n\n"
            "Respond with a JSON object: "
            '{"sentiment": "positive|negative|neutral", "score": 0.0-1.0, "summary": "..."}'
        )

        raw = await self._llm(
            messages=[{"role": "user", "content": prompt}],
            system="You are a sentiment analysis expert. Return only valid JSON.",
        )

        return AgentResult(
            agent_name=self.name,
            success=True,
            output={"raw": raw, "subject": subject},
        )
