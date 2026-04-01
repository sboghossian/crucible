"""Plugin discovery — from directories, entry_points, or explicit module paths."""

from __future__ import annotations

import importlib
import importlib.util
import logging
import os
import sys
from pathlib import Path
from typing import Any

from .hooks import HookRegistry, PluginHooks
from .registry import PluginManifest, PluginRegistry

logger = logging.getLogger(__name__)


class PluginLoader:
    """
    Discovers and loads plugins from multiple sources.

    Sources:
    - Directory: scans a folder for .py files and imports them.
      Any class decorated with @agent_plugin gets auto-registered.
    - Entry points: discovers packages that declare the 'crucible.plugins' group.
    - Explicit module path: loads a single 'module.ClassName' string.
    - Manifest: reads a plugin.yaml and loads the declared agents + hooks.
    """

    def __init__(
        self,
        plugin_registry: PluginRegistry | None = None,
        hook_registry: HookRegistry | None = None,
    ) -> None:
        self._plugins = plugin_registry or PluginRegistry.instance()
        self._hooks = hook_registry or HookRegistry.instance()

    # ------------------------------------------------------------------ #
    # Directory                                                            #
    # ------------------------------------------------------------------ #

    def load_from_directory(self, directory: str | Path) -> int:
        """
        Import every .py file in `directory`.

        Decorated classes are registered automatically by the @agent_plugin
        decorator as a side-effect of import. Returns the number of new files
        loaded.
        """
        directory = Path(directory)
        if not directory.is_dir():
            raise ValueError(f"Plugin directory does not exist: {directory}")

        loaded = 0
        for py_file in sorted(directory.glob("*.py")):
            if py_file.name.startswith("_"):
                continue
            module_name = f"_crucible_plugin_{py_file.stem}"
            spec = importlib.util.spec_from_file_location(module_name, py_file)
            if spec is None or spec.loader is None:
                logger.warning("Could not load plugin file: %s", py_file)
                continue
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            try:
                spec.loader.exec_module(module)  # type: ignore[union-attr]
                loaded += 1
                logger.debug("Loaded plugin module: %s", py_file.name)
            except Exception:
                logger.exception("Failed to load plugin file: %s", py_file)
        return loaded

    # ------------------------------------------------------------------ #
    # Installed entry_points                                              #
    # ------------------------------------------------------------------ #

    def load_from_entry_points(self, group: str = "crucible.plugins") -> int:
        """
        Discover plugins installed via Python packaging.

        Packages advertise plugins by declaring in their pyproject.toml::

            [project.entry-points."crucible.plugins"]
            my_plugin = "my_package.my_module"

        Returns the number of entry_points loaded.
        """
        try:
            from importlib.metadata import entry_points
            eps = entry_points(group=group)
        except Exception:
            logger.debug("Entry-point discovery not available")
            return 0

        loaded = 0
        for ep in eps:
            try:
                ep.load()
                loaded += 1
                logger.debug("Loaded plugin entry_point: %s", ep.name)
            except Exception:
                logger.exception("Failed to load entry_point: %s", ep.name)
        return loaded

    # ------------------------------------------------------------------ #
    # Explicit module path                                                 #
    # ------------------------------------------------------------------ #

    def load_from_module(self, dotted_path: str) -> type[Any] | None:
        """
        Load a single class from a dotted path like 'my_package.my_module.MyAgent'.

        If the path has no dot it is treated as a bare module (all decorated
        classes in that module are registered as a side-effect).
        """
        if "." not in dotted_path:
            try:
                importlib.import_module(dotted_path)
                return None
            except ImportError:
                logger.exception("Cannot import module: %s", dotted_path)
                return None

        module_path, class_name = dotted_path.rsplit(".", 1)
        try:
            module = importlib.import_module(module_path)
        except ImportError:
            logger.exception("Cannot import module: %s", module_path)
            return None

        cls = getattr(module, class_name, None)
        if cls is None:
            logger.error("Class '%s' not found in module '%s'", class_name, module_path)
            return None

        # Auto-register if not already decorated
        if not any(r.cls is cls for r in self._plugins.list_plugins()):
            self._plugins.register(
                cls=cls,
                name=class_name,
                description=getattr(cls, "__doc__", "") or "",
                source="explicit",
            )
            logger.debug("Registered plugin from explicit path: %s", dotted_path)

        return cls

    # ------------------------------------------------------------------ #
    # Manifest                                                             #
    # ------------------------------------------------------------------ #

    def load_from_manifest(self, manifest_path: str | Path) -> PluginManifest:
        """
        Load agents and hooks declared in a plugin.yaml manifest.

        The manifest directory is added to sys.path so that relative
        module imports work correctly.
        """
        manifest_path = Path(manifest_path)
        manifest = PluginManifest.from_file(str(manifest_path))
        plugin_dir = str(manifest_path.parent)

        if plugin_dir not in sys.path:
            sys.path.insert(0, plugin_dir)

        # Load agents
        for agent_spec in manifest.agents:
            module_name = agent_spec.get("module", "")
            class_name = agent_spec.get("class", "")
            if module_name and class_name:
                self.load_from_module(f"{module_name}.{class_name}")

        # Load hooks
        hook_callables: dict[str, Any] = {}
        for hook_name, dotted in manifest.hooks.items():
            if "." not in dotted:
                continue
            mod_path, fn_name = dotted.rsplit(".", 1)
            try:
                mod = importlib.import_module(mod_path)
                fn = getattr(mod, fn_name, None)
                if fn is not None:
                    hook_callables[hook_name] = fn
            except ImportError:
                logger.exception("Cannot import hook: %s", dotted)

        if hook_callables:
            self._hooks.register_from_callables(manifest.name, hook_callables)

        logger.info("Loaded plugin manifest: %s v%s", manifest.name, manifest.version)
        return manifest


# ------------------------------------------------------------------ #
# Hot-reload watcher                                                  #
# ------------------------------------------------------------------ #

class PluginWatcher:
    """
    Watches a directory for file changes and reloads plugins on modification.

    Uses a background thread with polling (no external dependencies).
    Call `start()` to begin watching and `stop()` to shut down.

    Note: hot-reload replaces existing registrations in-place.
    """

    def __init__(
        self,
        directory: str | Path,
        poll_interval: float = 1.0,
        plugin_registry: PluginRegistry | None = None,
        hook_registry: HookRegistry | None = None,
    ) -> None:
        self._directory = Path(directory)
        self._poll_interval = poll_interval
        self._loader = PluginLoader(
            plugin_registry=plugin_registry,
            hook_registry=hook_registry,
        )
        self._mtimes: dict[Path, float] = {}
        self._thread: Any = None
        self._stop_event: Any = None

    def start(self) -> None:
        import threading
        self._stop_event = threading.Event()
        self._thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread.start()
        logger.info("Plugin watcher started for: %s", self._directory)

    def stop(self) -> None:
        if self._stop_event:
            self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=5)
        logger.info("Plugin watcher stopped")

    def _watch_loop(self) -> None:
        import time
        while not self._stop_event.is_set():  # type: ignore[union-attr]
            self._check_for_changes()
            time.sleep(self._poll_interval)

    def _check_for_changes(self) -> None:
        for py_file in self._directory.glob("*.py"):
            if py_file.name.startswith("_"):
                continue
            try:
                mtime = py_file.stat().st_mtime
            except OSError:
                continue
            if self._mtimes.get(py_file) != mtime:
                self._mtimes[py_file] = mtime
                self._reload_file(py_file)

    def _reload_file(self, py_file: Path) -> None:
        module_name = f"_crucible_plugin_{py_file.stem}"
        logger.info("Hot-reloading plugin: %s", py_file.name)

        if module_name in sys.modules:
            try:
                importlib.reload(sys.modules[module_name])
            except Exception:
                logger.exception("Failed to reload plugin: %s", py_file.name)
        else:
            spec = importlib.util.spec_from_file_location(module_name, py_file)
            if spec is None or spec.loader is None:
                return
            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            try:
                spec.loader.exec_module(module)  # type: ignore[union-attr]
            except Exception:
                logger.exception("Failed to load plugin: %s", py_file.name)
