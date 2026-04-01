"""@agent_plugin decorator for registering custom agents."""

from __future__ import annotations

from typing import Any

from .registry import PluginRegistry


def agent_plugin(
    name: str,
    description: str = "",
    version: str = "1.0.0",
    author: str = "",
) -> Any:
    """
    Decorator that registers a BaseAgent subclass as a Crucible plugin.

    Example::

        from crucible.plugins import agent_plugin
        from crucible.core.agent import BaseAgent, AgentResult

        @agent_plugin(
            name="my_custom_agent",
            description="Does something cool",
            version="1.0.0",
        )
        class MyAgent(BaseAgent):
            async def run(self, **kwargs):
                return AgentResult(agent_name=self.name, success=True, output="done")
    """
    def decorator(cls: type[Any]) -> type[Any]:
        # Patch the class name attribute so BaseAgent.name works
        if not hasattr(cls, "name") or cls.name == "base_agent":
            cls.name = name

        PluginRegistry.instance().register(
            cls=cls,
            name=name,
            description=description,
            version=version,
            author=author,
            source="decorator",
        )
        return cls

    return decorator
