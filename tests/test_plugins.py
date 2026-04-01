"""Tests for the Plugin API — registration, discovery, hooks, and hot-reload."""

from __future__ import annotations

import asyncio
import importlib
import sys
import tempfile
import textwrap
import uuid
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from crucible.core.agent import AgentConfig, AgentResult, BaseAgent
from crucible.core.events import EventBus
from crucible.core.state import SharedState
from crucible.plugins.decorators import agent_plugin
from crucible.plugins.hooks import HookRegistry, PluginHooks
from crucible.plugins.loader import PluginLoader, PluginWatcher
from crucible.plugins.registry import PluginManifest, PluginRegistration, PluginRegistry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_state() -> SharedState:
    return SharedState(run_id=str(uuid.uuid4())[:8], subject="test")


def make_mock_client(text: str = "ok") -> Any:
    msg = MagicMock()
    msg.content = [MagicMock(text=text)]
    client = MagicMock()
    client.messages.create = AsyncMock(return_value=msg)
    return client


def fresh_registry() -> PluginRegistry:
    PluginRegistry.reset()
    return PluginRegistry.instance()


def fresh_hooks() -> HookRegistry:
    HookRegistry.reset()
    return HookRegistry.instance()


# ---------------------------------------------------------------------------
# PluginRegistry unit tests
# ---------------------------------------------------------------------------


class TestPluginRegistry:
    def setup_method(self) -> None:
        fresh_registry()

    def test_singleton(self) -> None:
        a = PluginRegistry.instance()
        b = PluginRegistry.instance()
        assert a is b

    def test_register_and_get(self) -> None:
        reg = PluginRegistry.instance()

        class DummyAgent(BaseAgent):
            name = "dummy"
            async def run(self, **kwargs: Any) -> AgentResult:
                return AgentResult(agent_name=self.name, success=True, output=None)

        registration = reg.register(DummyAgent, name="dummy", description="A dummy", version="2.0.0")
        assert registration.name == "dummy"
        assert registration.version == "2.0.0"
        assert reg.get("dummy") is registration

    def test_list_plugins(self) -> None:
        reg = PluginRegistry.instance()

        class A(BaseAgent):
            name = "a"
            async def run(self, **kwargs: Any) -> AgentResult:
                return AgentResult(agent_name=self.name, success=True, output=None)

        class B(BaseAgent):
            name = "b"
            async def run(self, **kwargs: Any) -> AgentResult:
                return AgentResult(agent_name=self.name, success=True, output=None)

        reg.register(A, name="a")
        reg.register(B, name="b")
        names = {p.name for p in reg.list_plugins()}
        assert "a" in names
        assert "b" in names

    def test_overwrite_logs_warning(self, caplog: Any) -> None:
        reg = PluginRegistry.instance()

        class C(BaseAgent):
            name = "c"
            async def run(self, **kwargs: Any) -> AgentResult:
                return AgentResult(agent_name=self.name, success=True, output=None)

        reg.register(C, name="c")
        with caplog.at_level("WARNING"):
            reg.register(C, name="c")
        assert any("already registered" in r.message for r in caplog.records)

    def test_clear(self) -> None:
        reg = PluginRegistry.instance()

        class D(BaseAgent):
            name = "d"
            async def run(self, **kwargs: Any) -> AgentResult:
                return AgentResult(agent_name=self.name, success=True, output=None)

        reg.register(D, name="d")
        assert len(reg) == 1
        reg.clear()
        assert len(reg) == 0


# ---------------------------------------------------------------------------
# @agent_plugin decorator
# ---------------------------------------------------------------------------


class TestAgentPluginDecorator:
    def setup_method(self) -> None:
        fresh_registry()

    def test_decorator_registers(self) -> None:
        @agent_plugin(name="decorated", description="test decorator", version="3.0.0")
        class MyAgent(BaseAgent):
            async def run(self, **kwargs: Any) -> AgentResult:
                return AgentResult(agent_name=self.name, success=True, output=None)

        reg = PluginRegistry.instance().get("decorated")
        assert reg is not None
        assert reg.name == "decorated"
        assert reg.version == "3.0.0"
        assert reg.description == "test decorator"
        assert reg.source == "decorator"

    def test_decorator_sets_class_name(self) -> None:
        @agent_plugin(name="named_agent")
        class AnotherAgent(BaseAgent):
            async def run(self, **kwargs: Any) -> AgentResult:
                return AgentResult(agent_name=self.name, success=True, output=None)

        assert AnotherAgent.name == "named_agent"

    def test_decorator_returns_class_unchanged(self) -> None:
        original_module = "test_module"

        @agent_plugin(name="passthrough")
        class PassthroughAgent(BaseAgent):
            async def run(self, **kwargs: Any) -> AgentResult:
                return AgentResult(agent_name=self.name, success=True, output=None)

        assert issubclass(PassthroughAgent, BaseAgent)


# ---------------------------------------------------------------------------
# Directory discovery
# ---------------------------------------------------------------------------


class TestDirectoryDiscovery:
    def setup_method(self) -> None:
        fresh_registry()

    def test_load_from_directory(self, tmp_path: Path) -> None:
        plugin_code = textwrap.dedent("""\
            from crucible.plugins import agent_plugin
            from crucible.core.agent import BaseAgent, AgentResult
            from typing import Any

            @agent_plugin(name="dir_agent", description="from directory", version="1.0.0")
            class DirAgent(BaseAgent):
                name = "dir_agent"
                async def run(self, **kwargs: Any) -> AgentResult:
                    return AgentResult(agent_name=self.name, success=True, output="dir")
        """)
        (tmp_path / "dir_plugin.py").write_text(plugin_code)

        loader = PluginLoader()
        count = loader.load_from_directory(tmp_path)

        assert count == 1
        reg = PluginRegistry.instance().get("dir_agent")
        assert reg is not None
        assert reg.description == "from directory"

    def test_load_from_directory_skips_dunder(self, tmp_path: Path) -> None:
        (tmp_path / "__init__.py").write_text("# init")
        (tmp_path / "__helper__.py").write_text("# helper")
        (tmp_path / "real_plugin.py").write_text(textwrap.dedent("""\
            from crucible.plugins import agent_plugin
            from crucible.core.agent import BaseAgent, AgentResult
            from typing import Any

            @agent_plugin(name="real", description="real")
            class RealAgent(BaseAgent):
                name = "real"
                async def run(self, **kwargs: Any) -> AgentResult:
                    return AgentResult(agent_name=self.name, success=True, output=None)
        """))

        loader = PluginLoader()
        count = loader.load_from_directory(tmp_path)
        assert count == 1

    def test_load_from_directory_bad_path_raises(self) -> None:
        loader = PluginLoader()
        with pytest.raises(ValueError, match="does not exist"):
            loader.load_from_directory("/nonexistent_crucible_test_dir")

    def test_load_from_directory_ignores_broken_files(self, tmp_path: Path, caplog: Any) -> None:
        (tmp_path / "broken.py").write_text("this is not valid python !!!@@@")
        loader = PluginLoader()
        with caplog.at_level("ERROR"):
            count = loader.load_from_directory(tmp_path)
        assert count == 0


# ---------------------------------------------------------------------------
# Explicit module path
# ---------------------------------------------------------------------------


class TestLoadFromModule:
    def setup_method(self) -> None:
        fresh_registry()

    def test_load_explicit_module_class(self) -> None:
        # Register a fake module in sys.modules
        fake_mod_name = "_crucible_test_explicit_mod"

        class ExplicitAgent(BaseAgent):
            name = "explicit_agent"
            async def run(self, **kwargs: Any) -> AgentResult:
                return AgentResult(agent_name=self.name, success=True, output=None)

        fake_mod = MagicMock()
        fake_mod.ExplicitAgent = ExplicitAgent
        sys.modules[fake_mod_name] = fake_mod

        loader = PluginLoader()
        result = loader.load_from_module(f"{fake_mod_name}.ExplicitAgent")
        assert result is ExplicitAgent
        assert PluginRegistry.instance().get("ExplicitAgent") is not None

        del sys.modules[fake_mod_name]

    def test_load_missing_class(self, caplog: Any) -> None:
        fake_mod_name = "_crucible_test_no_class"
        fake_mod = MagicMock(spec=[])
        sys.modules[fake_mod_name] = fake_mod

        loader = PluginLoader()
        with caplog.at_level("ERROR"):
            result = loader.load_from_module(f"{fake_mod_name}.NoSuchClass")
        assert result is None

        del sys.modules[fake_mod_name]


# ---------------------------------------------------------------------------
# Plugin manifest (plugin.yaml)
# ---------------------------------------------------------------------------


class TestPluginManifest:
    def test_manifest_from_file(self, tmp_path: Path) -> None:
        yaml_content = textwrap.dedent("""\
            name: test-plugin
            version: 2.1.0
            description: Test manifest
            author: Steph
            agents:
              - class: FooAgent
                module: foo_module
            hooks:
              before_run: foo_hooks.setup
        """)
        manifest_file = tmp_path / "plugin.yaml"
        manifest_file.write_text(yaml_content)

        manifest = PluginManifest.from_file(str(manifest_file))
        assert manifest.name == "test-plugin"
        assert manifest.version == "2.1.0"
        assert manifest.author == "Steph"
        assert manifest.agents[0]["class"] == "FooAgent"
        assert manifest.hooks["before_run"] == "foo_hooks.setup"

    def test_load_from_manifest_registers_agents(self, tmp_path: Path) -> None:
        fresh_registry()
        fresh_hooks()

        agent_code = textwrap.dedent("""\
            from crucible.plugins import agent_plugin
            from crucible.core.agent import BaseAgent, AgentResult
            from typing import Any

            @agent_plugin(name="manifest_agent", description="from manifest")
            class ManifestAgent(BaseAgent):
                name = "manifest_agent"
                async def run(self, **kwargs: Any) -> AgentResult:
                    return AgentResult(agent_name=self.name, success=True, output=None)
        """)
        (tmp_path / "manifest_mod.py").write_text(agent_code)

        yaml_content = textwrap.dedent(f"""\
            name: manifest-test
            version: 1.0.0
            description: manifest test
            agents:
              - class: ManifestAgent
                module: manifest_mod
        """)
        (tmp_path / "plugin.yaml").write_text(yaml_content)

        loader = PluginLoader()
        manifest = loader.load_from_manifest(tmp_path / "plugin.yaml")

        assert manifest.name == "manifest-test"
        assert PluginRegistry.instance().get("manifest_agent") is not None

    def test_load_from_manifest_registers_hooks(self, tmp_path: Path) -> None:
        fresh_registry()
        hooks = fresh_hooks()

        hooks_code = textwrap.dedent("""\
            async def setup(**kwargs):
                pass
        """)
        (tmp_path / "hook_mod.py").write_text(hooks_code)
        (tmp_path / "stub_agent_mod.py").write_text("# empty")

        yaml_content = textwrap.dedent("""\
            name: hooks-test
            version: 1.0.0
            description: hooks test
            agents: []
            hooks:
              before_run: hook_mod.setup
        """)
        (tmp_path / "plugin.yaml").write_text(yaml_content)

        loader = PluginLoader()
        loader.load_from_manifest(tmp_path / "plugin.yaml")

        assert len(hooks._hooks["before_run"]) == 1


# ---------------------------------------------------------------------------
# Lifecycle hooks
# ---------------------------------------------------------------------------


class TestLifecycleHooks:
    def setup_method(self) -> None:
        fresh_hooks()

    @pytest.mark.asyncio
    async def test_before_run_fires(self) -> None:
        called: list[str] = []

        async def hook(**kwargs: Any) -> None:
            called.append("before_run")

        hooks = HookRegistry.instance()
        hooks.register_hooks("test_plugin", PluginHooks(before_run=hook))
        await hooks.fire("before_run", subject="test")
        assert called == ["before_run"]

    @pytest.mark.asyncio
    async def test_after_run_fires(self) -> None:
        called: list[str] = []

        async def hook(**kwargs: Any) -> None:
            called.append("after_run")

        hooks = HookRegistry.instance()
        hooks.register_hooks("test_plugin", PluginHooks(after_run=hook))
        await hooks.fire("after_run")
        assert called == ["after_run"]

    @pytest.mark.asyncio
    async def test_on_error_fires(self) -> None:
        errors: list[str] = []

        async def hook(**kwargs: Any) -> None:
            errors.append(kwargs.get("error", ""))

        hooks = HookRegistry.instance()
        hooks.register_hooks("test_plugin", PluginHooks(on_error=hook))
        await hooks.fire("on_error", error="something went wrong")
        assert errors == ["something went wrong"]

    @pytest.mark.asyncio
    async def test_on_debate_fires(self) -> None:
        topics: list[str] = []

        def sync_hook(**kwargs: Any) -> None:
            topics.append(kwargs.get("topic", ""))

        hooks = HookRegistry.instance()
        hooks.register_hooks("test_plugin", PluginHooks(on_debate=sync_hook))
        await hooks.fire("on_debate", topic="Should we refactor?")
        assert topics == ["Should we refactor?"]

    @pytest.mark.asyncio
    async def test_hook_error_does_not_propagate(self) -> None:
        """A crashing hook must not crash the caller."""
        async def bad_hook(**kwargs: Any) -> None:
            raise RuntimeError("hook exploded")

        hooks = HookRegistry.instance()
        hooks.register_hooks("test_plugin", PluginHooks(before_run=bad_hook))
        # Must not raise
        await hooks.fire("before_run", subject="test")

    @pytest.mark.asyncio
    async def test_multiple_hooks_all_fire(self) -> None:
        order: list[int] = []

        async def first(**kwargs: Any) -> None:
            order.append(1)

        async def second(**kwargs: Any) -> None:
            order.append(2)

        hooks = HookRegistry.instance()
        hooks.register_hooks("p1", PluginHooks(before_run=first))
        hooks.register_hooks("p2", PluginHooks(before_run=second))
        await hooks.fire("before_run")
        assert order == [1, 2]


# ---------------------------------------------------------------------------
# Hot-reload watcher
# ---------------------------------------------------------------------------


class TestHotReload:
    def setup_method(self) -> None:
        fresh_registry()

    def test_watcher_detects_new_file(self, tmp_path: Path) -> None:
        import time

        watcher = PluginWatcher(tmp_path, poll_interval=0.05)
        watcher.start()

        try:
            plugin_code = textwrap.dedent("""\
                from crucible.plugins import agent_plugin
                from crucible.core.agent import BaseAgent, AgentResult
                from typing import Any

                @agent_plugin(name="hot_agent", description="hot reload test")
                class HotAgent(BaseAgent):
                    name = "hot_agent"
                    async def run(self, **kwargs: Any) -> AgentResult:
                        return AgentResult(agent_name=self.name, success=True, output=None)
            """)
            (tmp_path / "hot_plugin.py").write_text(plugin_code)

            # Give the watcher time to detect and load the file
            deadline = time.time() + 3.0
            while time.time() < deadline:
                if PluginRegistry.instance().get("hot_agent") is not None:
                    break
                time.sleep(0.1)

            assert PluginRegistry.instance().get("hot_agent") is not None
        finally:
            watcher.stop()

    def test_watcher_stop(self, tmp_path: Path) -> None:
        watcher = PluginWatcher(tmp_path, poll_interval=0.05)
        watcher.start()
        watcher.stop()
        assert watcher._stop_event.is_set()


# ---------------------------------------------------------------------------
# Orchestrator plugin integration
# ---------------------------------------------------------------------------


class TestOrchestratorPluginIntegration:
    def setup_method(self) -> None:
        fresh_registry()
        fresh_hooks()

    def test_register_plugin_on_orchestrator(self) -> None:
        from crucible.core.orchestrator import Orchestrator

        orch = Orchestrator(api_key="test")

        class SimpleAgent(BaseAgent):
            name = "simple"
            async def run(self, **kwargs: Any) -> AgentResult:
                return AgentResult(agent_name=self.name, success=True, output="simple")

        orch.register_plugin(SimpleAgent, name="simple")
        assert "simple" in orch._plugin_classes

    def test_load_plugins_from_directory(self, tmp_path: Path) -> None:
        from crucible.core.orchestrator import Orchestrator

        plugin_code = textwrap.dedent("""\
            from crucible.plugins import agent_plugin
            from crucible.core.agent import BaseAgent, AgentResult
            from typing import Any

            @agent_plugin(name="orch_plugin", description="orch test")
            class OrchPlugin(BaseAgent):
                name = "orch_plugin"
                async def run(self, **kwargs: Any) -> AgentResult:
                    return AgentResult(agent_name=self.name, success=True, output=None)
        """)
        (tmp_path / "orch_plugin.py").write_text(plugin_code)

        orch = Orchestrator(api_key="test")
        orch.load_plugins_from(str(tmp_path))
        assert "orch_plugin" in orch._plugin_classes

    def test_sync_plugins_from_global_registry(self) -> None:
        from crucible.core.orchestrator import Orchestrator

        class GlobalAgent(BaseAgent):
            name = "global_agent"
            async def run(self, **kwargs: Any) -> AgentResult:
                return AgentResult(agent_name=self.name, success=True, output=None)

        PluginRegistry.instance().register(GlobalAgent, name="global_agent")

        orch = Orchestrator(api_key="test")
        orch.sync_plugins_from_registry()
        assert "global_agent" in orch._plugin_classes
