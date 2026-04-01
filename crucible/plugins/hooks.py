"""Lifecycle hooks for plugins — before_run, after_run, on_error, on_debate."""

from __future__ import annotations

import logging
from collections.abc import Callable, Awaitable
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

HookFn = Callable[..., Awaitable[None] | None]


@dataclass
class PluginHooks:
    """Collection of lifecycle hook callables for a single plugin."""

    before_run: HookFn | None = None
    after_run: HookFn | None = None
    on_error: HookFn | None = None
    on_debate: HookFn | None = None


class HookRegistry:
    """
    Global registry of plugin lifecycle hooks.

    Hooks are invoked by the Orchestrator at the appropriate lifecycle points.
    Each hook is a sync or async callable that receives keyword arguments
    describing the event context.
    """

    _instance: HookRegistry | None = None

    def __init__(self) -> None:
        self._hooks: dict[str, list[HookFn]] = {
            "before_run": [],
            "after_run": [],
            "on_error": [],
            "on_debate": [],
        }

    @classmethod
    def instance(cls) -> "HookRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        cls._instance = None

    def register_hooks(self, plugin_name: str, hooks: PluginHooks) -> None:
        for event in ("before_run", "after_run", "on_error", "on_debate"):
            fn = getattr(hooks, event, None)
            if fn is not None:
                self._hooks[event].append(fn)
                logger.debug("Registered %s hook from plugin '%s'", event, plugin_name)

    def register_from_callables(self, plugin_name: str, hooks_dict: dict[str, HookFn]) -> None:
        for event, fn in hooks_dict.items():
            if event in self._hooks:
                self._hooks[event].append(fn)
                logger.debug("Registered %s hook from plugin '%s'", event, plugin_name)

    async def fire(self, event: str, **kwargs: Any) -> None:
        """Fire all hooks registered for `event`. Errors are logged, not raised."""
        import asyncio
        for fn in self._hooks.get(event, []):
            try:
                result = fn(**kwargs)
                if asyncio.iscoroutine(result):
                    await result
            except Exception:
                logger.exception("Hook %s raised an error", event)

    def clear(self) -> None:
        for key in self._hooks:
            self._hooks[key].clear()
