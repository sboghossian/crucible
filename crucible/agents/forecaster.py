"""Predictive analysis agent — generates forecasts with confidence scores."""

from __future__ import annotations

from typing import Any

from ..core.agent import AgentResult, BaseAgent
from ..core.state import ForecastResult


class ForecasterAgent(BaseAgent):
    """
    Generates probabilistic forecasts and trend analysis based on
    the accumulated research findings, scan data, and debate outcomes.
    """

    name = "forecaster"

    @property
    def system_prompt(self) -> str:
        return (
            "You are a superforecaster with expertise in technology trends, software ecosystems, "
            "and organizational dynamics. You make specific, falsifiable predictions with explicit "
            "probability estimates. You distinguish between base rates, inside view, and outside view. "
            "You cite reference classes and analogies. You are calibrated — 70% predictions should "
            "be right about 70% of the time. You never hedge into meaninglessness."
        )

    async def run(self, subject: str, horizon: str = "12 months", **_: Any) -> AgentResult:
        state = await self._state.get()

        context_parts = [f"Subject: {subject}", f"Forecast horizon: {horizon}"]

        if state.research:
            context_parts.append(f"Research synthesis: {state.research.synthesis[:400]}")
        if state.debate:
            context_parts.append(
                f"Debate conclusion ({state.debate.winner}): "
                f"{state.debate.decision[:300] if state.debate.decision else 'N/A'}"
            )
        if state.patterns:
            recs = "; ".join(state.patterns.recommendations[:3])
            context_parts.append(f"Key patterns: {recs}")

        context = "\n\n".join(context_parts)

        # Generate predictions
        predictions_prompt = f"""{context}

---
Generate 5 specific, falsifiable predictions for the next {horizon}.

For each prediction:
PREDICTION [N]: <specific, measurable claim>
PROBABILITY: <0-100%>
REFERENCE CLASS: <comparable historical examples>
KEY ASSUMPTION: <the main thing that must be true for this to happen>
DISCONFIRMING EVIDENCE: <what would tell us this prediction is wrong>"""

        predictions_text = await self._llm([{"role": "user", "content": predictions_prompt}])

        # Generate risks and opportunities
        ro_prompt = f"""{context}

Based on the above, identify:
- 3 KEY RISKS (events with high impact if they occur, even if low probability)
- 3 KEY OPPORTUNITIES (asymmetric upside scenarios)

For risks: RISK [N]: <name> | PROBABILITY: X% | IMPACT: <description>
For opportunities: OPPORTUNITY [N]: <name> | PROBABILITY: X% | UPSIDE: <description>"""

        ro_text = await self._llm([{"role": "user", "content": ro_prompt}])

        predictions = self._parse_predictions(predictions_text)
        risks = self._parse_items(ro_text, "RISK")
        opportunities = self._parse_items(ro_text, "OPPORTUNITY")

        # Compute aggregate confidence
        probs = [p.get("probability", 50) for p in predictions]
        avg_confidence = sum(probs) / len(probs) / 100 if probs else 0.5

        result = ForecastResult(
            horizon=horizon,
            predictions=predictions,
            confidence=round(avg_confidence, 2),
            key_risks=risks,
            opportunities=opportunities,
        )

        await self._state.set_typed("forecast", result)

        return AgentResult(
            agent_name=self.name,
            success=True,
            output=result.model_dump(),
        )

    def _parse_predictions(self, text: str) -> list[dict[str, Any]]:
        predictions: list[dict[str, Any]] = []
        current: dict[str, Any] = {}

        for line in text.split("\n"):
            line = line.strip()
            if line.upper().startswith("PREDICTION") and ":" in line:
                if current:
                    predictions.append(current)
                current = {"claim": line.split(":", 1)[1].strip()}
            elif line.upper().startswith("PROBABILITY") and ":" in line and current:
                prob_str = line.split(":", 1)[1].strip().rstrip("%")
                try:
                    current["probability"] = float(prob_str)
                except ValueError:
                    current["probability"] = 50.0
            elif line.upper().startswith("KEY ASSUMPTION") and ":" in line and current:
                current["assumption"] = line.split(":", 1)[1].strip()
            elif line.upper().startswith("REFERENCE CLASS") and ":" in line and current:
                current["reference_class"] = line.split(":", 1)[1].strip()

        if current:
            predictions.append(current)

        return predictions

    def _parse_items(self, text: str, prefix: str) -> list[str]:
        items: list[str] = []
        for line in text.split("\n"):
            line = line.strip()
            if line.upper().startswith(prefix) and ":" in line:
                item = line.split(":", 1)[1].strip()
                if item:
                    items.append(item)
        return items
