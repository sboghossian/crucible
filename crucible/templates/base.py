"""Base types for the Crucible template marketplace."""

from __future__ import annotations

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from ..core.agent import AgentConfig, AgentResult, BaseAgent
from ..core.events import EventBus
from ..core.state import SharedState

import logging

logger = logging.getLogger(__name__)

# Global registry populated by the @template decorator
_REGISTRY: dict[str, "Template"] = {}


@dataclass
class AgentSpec:
    """Declarative specification of a single agent in a template."""

    name: str
    role: str
    instructions: str
    config: AgentConfig = field(default_factory=AgentConfig)


@dataclass
class Template:
    """A complete, ready-to-deploy agent team configuration."""

    name: str
    description: str
    category: str
    agents: list[AgentSpec]
    debate_topics: list[str]
    expected_outputs: list[str]
    tags: list[str] = field(default_factory=list)
    version: str = "1.0.0"


def template(t: Template) -> Template:
    """Decorator / registration function — adds the template to the global registry."""
    _REGISTRY[t.name] = t
    return t


class TemplateAgent(BaseAgent):
    """A generic agent driven entirely by its AgentSpec instructions."""

    def __init__(
        self,
        spec: AgentSpec,
        client: Any,
        state: SharedState,
        bus: EventBus,
    ) -> None:
        super().__init__(client=client, state=state, bus=bus, config=spec.config)
        self.name = spec.name
        self._spec = spec

    @property
    def system_prompt(self) -> str:
        return self._spec.instructions

    async def run(self, **kwargs: Any) -> AgentResult:
        subject = kwargs.get("subject", "")
        context = kwargs.get("context", "")
        extra = "\n".join(f"{k}: {v}" for k, v in kwargs.items() if k not in ("subject", "context"))
        user_msg = f"Subject: {subject}\n\nContext: {context}"
        if extra:
            user_msg += f"\n\nAdditional inputs:\n{extra}"
        user_msg += "\n\nComplete your assigned role thoroughly. Be specific and actionable."

        output = await self._llm([{"role": "user", "content": user_msg}])
        return AgentResult(agent_name=self.name, success=True, output=output)


class TemplateSession:
    """
    A configured, ready-to-run agent team spun up from a Template.

    Usage::

        session = registry.deploy_template("seo_article", api_key="...")
        results = await session.run(subject="10x Your Landing Page Conversions")
    """

    def __init__(
        self,
        template: Template,
        api_key: str | None = None,
        model: str | None = None,
    ) -> None:
        self.template = template
        self._api_key = api_key
        self._model = model

    def plan(self) -> dict[str, Any]:
        """Return the deployment plan without executing anything."""
        return {
            "template": self.template.name,
            "category": self.template.category,
            "description": self.template.description,
            "agents": [
                {"name": s.name, "role": s.role}
                for s in self.template.agents
            ],
            "debate_topics": self.template.debate_topics,
            "expected_outputs": self.template.expected_outputs,
            "tags": self.template.tags,
        }

    async def run(self, subject: str = "", **kwargs: Any) -> dict[str, Any]:
        """
        Execute the full agent team and optional debate council.

        Returns a dict keyed by agent name with their outputs, plus a
        ``_debate`` key if debate topics were configured.
        """
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=self._api_key)
        run_id = str(uuid.uuid4())
        state = SharedState(run_id=run_id, subject=subject or self.template.name)
        bus = EventBus()

        agents = [
            TemplateAgent(spec=spec, client=client, state=state, bus=bus)
            for spec in self.template.agents
        ]

        logger.info(
            "Deploying template '%s' with %d agents (run_id=%s)",
            self.template.name, len(agents), run_id,
        )

        results: dict[str, Any] = {}

        # Run all specialist agents concurrently
        tasks = [
            agent.execute(subject=subject, context=str(kwargs))
            for agent in agents
        ]
        completed = await asyncio.gather(*tasks, return_exceptions=True)

        for agent, outcome in zip(agents, completed):
            if isinstance(outcome, Exception):
                results[agent.name] = {"success": False, "error": str(outcome)}
            else:
                results[agent.name] = {
                    "success": outcome.success,
                    "output": outcome.output,
                    "duration_seconds": outcome.duration_seconds,
                }

        # Run debate council if topics are defined
        if self.template.debate_topics:
            try:
                from ..agents.debate_council import DebateCouncilAgent
                from ..core.agent import AgentConfig as AC

                dc = DebateCouncilAgent(
                    client=client,
                    state=state,
                    bus=bus,
                    config=AC(model=self._model or "claude-opus-4-6"),
                )
                agent_outputs_summary = "\n\n".join(
                    f"[{name}]: {str(data.get('output', ''))[:800]}"
                    for name, data in results.items()
                )
                topic = self.template.debate_topics[0]
                options = self.template.debate_topics[1:] if len(self.template.debate_topics) > 1 else []
                debate_result = await dc.execute(
                    topic=topic,
                    options=options,
                    context=f"Template: {self.template.name}\nSubject: {subject}\n\n{agent_outputs_summary}",
                )
                results["_debate"] = {
                    "success": debate_result.success,
                    "output": debate_result.output,
                }
            except Exception as exc:
                logger.warning("Debate council skipped: %s", exc)
                results["_debate"] = {"success": False, "error": str(exc)}

        results["_meta"] = {
            "template": self.template.name,
            "run_id": run_id,
            "subject": subject,
            "started_at": datetime.utcnow().isoformat(),
            "expected_outputs": self.template.expected_outputs,
        }

        return results
