"""Plugin registry — singleton that tracks all registered agent plugins."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

import yaml
from pydantic import BaseModel

if TYPE_CHECKING:
    from ..core.agent import BaseAgent

logger = logging.getLogger(__name__)


class PluginManifest(BaseModel):
    """Schema for plugin.yaml manifest files."""

    name: str
    version: str = "1.0.0"
    description: str = ""
    author: str = ""
    agents: list[dict[str, str]] = []
    hooks: dict[str, str] = {}

    @classmethod
    def from_file(cls, path: str) -> "PluginManifest":
        with open(path) as f:
            data = yaml.safe_load(f)
        return cls(**data)


@dataclass
class PluginRegistration:
    """Metadata + class reference for a registered plugin."""

    name: str
    cls: type[Any]  # subclass of BaseAgent
    description: str = ""
    version: str = "1.0.0"
    author: str = ""
    source: str = ""  # 'decorator', 'directory', 'entry_point', 'manifest'


class PluginRegistry:
    """
    Singleton registry of all registered agent plugins.

    Usage:
        registry = PluginRegistry.instance()
        registry.register(MyAgent, name="my_agent", description="...")
        registration = registry.get("my_agent")
        all_plugins = registry.list_plugins()
    """

    _instance: PluginRegistry | None = None

    def __init__(self) -> None:
        self._plugins: dict[str, PluginRegistration] = {}

    @classmethod
    def instance(cls) -> "PluginRegistry":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset singleton — used in tests."""
        cls._instance = None

    def register(
        self,
        cls: type[Any],
        name: str,
        description: str = "",
        version: str = "1.0.0",
        author: str = "",
        source: str = "decorator",
    ) -> PluginRegistration:
        if name in self._plugins:
            logger.warning("Plugin '%s' already registered — overwriting", name)
        reg = PluginRegistration(
            name=name,
            cls=cls,
            description=description,
            version=version,
            author=author,
            source=source,
        )
        self._plugins[name] = reg
        logger.debug("Registered plugin: %s (v%s)", name, version)
        return reg

    def get(self, name: str) -> PluginRegistration | None:
        return self._plugins.get(name)

    def list_plugins(self) -> list[PluginRegistration]:
        return list(self._plugins.values())

    def clear(self) -> None:
        """Remove all registrations — used in tests."""
        self._plugins.clear()

    def __len__(self) -> int:
        return len(self._plugins)
