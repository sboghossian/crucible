"""Crucible Plugin API — custom agent registration and discovery."""

from .decorators import agent_plugin
from .registry import PluginRegistry, PluginRegistration, PluginManifest
from .loader import PluginLoader
from .hooks import HookRegistry, PluginHooks

registry = PluginRegistry.instance()

__all__ = [
    "agent_plugin",
    "PluginRegistry",
    "PluginRegistration",
    "PluginManifest",
    "PluginLoader",
    "HookRegistry",
    "PluginHooks",
    "registry",
]
