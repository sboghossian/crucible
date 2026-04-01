"""Tests for the Template Composer — multi-stage pipelines."""

from __future__ import annotations

import asyncio
from typing import Any
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from crucible.templates.composer import (
    Pipeline,
    PipelineBuilder,
    PipelineStage,
    StageResult,
    _run_debate_gate,
)
from crucible.templates.pipelines import list_pipelines, get_pipeline


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_fake_session(outputs: dict[str, Any] | None = None) -> MagicMock:
    """Return a mock TemplateSession whose run() returns a canned dict."""
    if outputs is None:
        outputs = {
            "Agent A": {"success": True, "output": "Agent A output text"},
            "Agent B": {"success": True, "output": "Agent B output text"},
            "_meta": {"template": "fake", "run_id": "test-run"},
        }
    session = MagicMock()
    session.run = AsyncMock(return_value=outputs)
    return session


# ---------------------------------------------------------------------------
# PipelineStage
# ---------------------------------------------------------------------------

class TestPipelineStage:
    def test_defaults(self) -> None:
        stage = PipelineStage(template_name="market_research")
        assert stage.input_keys == []
        assert stage.output_keys == []
        assert stage.debate_gate is False
        assert stage.gate_topic == ""

    def test_debate_gate_auto_topic(self) -> None:
        stage = PipelineStage(
            template_name="product_spec",
            debate_gate=True,
        )
        assert "product_spec" in stage.gate_topic
        assert len(stage.gate_topic) > 0

    def test_explicit_gate_topic_preserved(self) -> None:
        stage = PipelineStage(
            template_name="web_app",
            debate_gate=True,
            gate_topic="Should we proceed with web app?",
        )
        assert stage.gate_topic == "Should we proceed with web app?"


# ---------------------------------------------------------------------------
# StageResult
# ---------------------------------------------------------------------------

class TestStageResult:
    def test_success_when_no_error(self) -> None:
        sr = StageResult(stage_index=0, template_name="t1", outputs={})
        assert sr.success is True

    def test_failure_when_error_set(self) -> None:
        sr = StageResult(stage_index=0, template_name="t1", outputs={}, error="boom")
        assert sr.success is False

    def test_context_for_next_stage_includes_all_non_meta(self) -> None:
        sr = StageResult(
            stage_index=0,
            template_name="stage_one",
            outputs={
                "Agent A": {"output": "hello"},
                "Agent B": {"output": "world"},
                "_meta": {"run_id": "x"},
            },
        )
        ctx = sr.context_for_next_stage([])
        assert "stage_one" in ctx
        assert "Agent A" in ctx
        assert "hello" in ctx
        assert "_meta" not in ctx

    def test_context_for_next_stage_filters_by_output_keys(self) -> None:
        sr = StageResult(
            stage_index=0,
            template_name="stage_one",
            outputs={
                "Agent A": {"output": "relevant"},
                "Agent B": {"output": "irrelevant"},
            },
        )
        ctx = sr.context_for_next_stage(["Agent A"])
        assert "relevant" in ctx
        assert "irrelevant" not in ctx


# ---------------------------------------------------------------------------
# PipelineBuilder
# ---------------------------------------------------------------------------

class TestPipelineBuilder:
    def test_fluent_chain(self) -> None:
        pipeline = (
            PipelineBuilder("my_pipe")
            .then("market_research")
            .then("product_spec", debate_gate=True)
            .then("web_app")
            .build()
        )
        assert pipeline.name == "my_pipe"
        assert len(pipeline.stages) == 3
        assert pipeline.stages[0].template_name == "market_research"
        assert pipeline.stages[1].template_name == "product_spec"
        assert pipeline.stages[1].debate_gate is True
        assert pipeline.stages[2].template_name == "web_app"

    def test_empty_pipeline_raises(self) -> None:
        with pytest.raises(ValueError, match="at least one stage"):
            PipelineBuilder("empty").build()

    def test_output_keys_propagated(self) -> None:
        pipeline = (
            PipelineBuilder("kw_pipe")
            .then("market_research", output_keys=["Report Writer"])
            .then("product_spec")
            .build()
        )
        assert pipeline.stages[0].output_keys == ["Report Writer"]

    def test_input_keys_propagated(self) -> None:
        pipeline = (
            PipelineBuilder("kw_pipe")
            .then("market_research")
            .then("product_spec", input_keys=["Market Analyst"])
            .build()
        )
        assert pipeline.stages[1].input_keys == ["Market Analyst"]


# ---------------------------------------------------------------------------
# Pipeline.run — unit tests with mocked sessions
# ---------------------------------------------------------------------------

class TestPipelineRun:
    def _make_registry_mock(self, fake_deploy: Any) -> MagicMock:
        """Return a mock _get_registry() return value that delegates to fake_deploy."""
        reg_mock = MagicMock()
        reg_mock.deploy_template.side_effect = fake_deploy
        get_reg_mock = MagicMock(return_value=reg_mock)
        return get_reg_mock

    @pytest.mark.asyncio
    async def test_stages_run_in_order(self) -> None:
        call_order: list[str] = []

        def fake_deploy(name: str, **_: Any) -> MagicMock:
            sess = MagicMock()

            async def _run(**kwargs: Any) -> dict[str, Any]:
                call_order.append(name)
                return {
                    "Agent": {"success": True, "output": f"{name} output"},
                    "_meta": {},
                }

            sess.run = _run
            return sess

        pipeline = (
            PipelineBuilder("order_test")
            .then("alpha")
            .then("beta")
            .then("gamma")
            .build()
        )

        with patch(
            "crucible.templates.composer._get_registry",
            self._make_registry_mock(fake_deploy),
        ):
            results = await pipeline.run(subject="test", api_key=None)

        assert call_order == ["alpha", "beta", "gamma"]
        assert len(results) == 3
        assert all(r.success for r in results)

    @pytest.mark.asyncio
    async def test_context_forwarded_between_stages(self) -> None:
        received_contexts: list[str] = []

        def fake_deploy(name: str, **_: Any) -> MagicMock:
            sess = MagicMock()

            async def _run(**kwargs: Any) -> dict[str, Any]:
                received_contexts.append(kwargs.get("context", ""))
                return {
                    "Agent": {"success": True, "output": f"{name} produced this output"},
                    "_meta": {},
                }

            sess.run = _run
            return sess

        pipeline = (
            PipelineBuilder("ctx_test")
            .then("stage_one")
            .then("stage_two")
            .build()
        )

        with patch(
            "crucible.templates.composer._get_registry",
            self._make_registry_mock(fake_deploy),
        ):
            results = await pipeline.run(subject="test", api_key=None)

        # First stage gets no context; second stage should receive stage_one's output
        assert received_contexts[0] == ""
        assert "stage_one produced this output" in received_contexts[1]

    @pytest.mark.asyncio
    async def test_pipeline_halts_on_failed_stage(self) -> None:
        call_count = 0

        def fake_deploy(name: str, **_: Any) -> MagicMock:
            sess = MagicMock()

            async def _run(**kwargs: Any) -> dict[str, Any]:
                nonlocal call_count
                call_count += 1
                if name == "stage_two":
                    raise RuntimeError("stage_two exploded")
                return {"Agent": {"success": True, "output": "ok"}, "_meta": {}}

            sess.run = _run
            return sess

        pipeline = (
            PipelineBuilder("halt_test")
            .then("stage_one")
            .then("stage_two")
            .then("stage_three")
            .build()
        )

        with patch(
            "crucible.templates.composer._get_registry",
            self._make_registry_mock(fake_deploy),
        ):
            results = await pipeline.run(subject="test", api_key=None)

        # Should stop after stage_two failure — stage_three never runs
        assert call_count == 2
        assert len(results) == 2
        assert results[1].success is False
        assert "stage_two exploded" in results[1].error

    @pytest.mark.asyncio
    async def test_debate_gate_halts_pipeline(self) -> None:
        call_order: list[str] = []

        def fake_deploy(name: str, **_: Any) -> MagicMock:
            sess = MagicMock()

            async def _run(**kwargs: Any) -> dict[str, Any]:
                call_order.append(name)
                return {"Agent": {"success": True, "output": "output"}, "_meta": {}}

            sess.run = _run
            return sess

        async def fake_gate(*_args: Any, **_kwargs: Any) -> tuple[bool, str]:
            return False, "Debate council decided to halt."

        pipeline = (
            PipelineBuilder("gate_test")
            .then("stage_one", debate_gate=True)
            .then("stage_two")
            .build()
        )

        with patch(
            "crucible.templates.composer._get_registry",
            self._make_registry_mock(fake_deploy),
        ), patch(
            "crucible.templates.composer._run_debate_gate",
            side_effect=fake_gate,
        ):
            results = await pipeline.run(subject="test", api_key=None)

        # stage_two should never run because gate halted after stage_one
        assert call_order == ["stage_one"]
        assert len(results) == 1
        assert results[0].gate_passed is False
        assert "halt" in results[0].gate_decision.lower()

    @pytest.mark.asyncio
    async def test_debate_gate_proceed_continues_pipeline(self) -> None:
        call_order: list[str] = []

        def fake_deploy(name: str, **_: Any) -> MagicMock:
            sess = MagicMock()

            async def _run(**kwargs: Any) -> dict[str, Any]:
                call_order.append(name)
                return {"Agent": {"success": True, "output": "ok"}, "_meta": {}}

            sess.run = _run
            return sess

        async def fake_gate(*_args: Any, **_kwargs: Any) -> tuple[bool, str]:
            return True, "Proceed with confidence."

        pipeline = (
            PipelineBuilder("gate_proceed_test")
            .then("stage_one", debate_gate=True)
            .then("stage_two")
            .build()
        )

        with patch(
            "crucible.templates.composer._get_registry",
            self._make_registry_mock(fake_deploy),
        ), patch(
            "crucible.templates.composer._run_debate_gate",
            side_effect=fake_gate,
        ):
            results = await pipeline.run(subject="test", api_key=None)

        assert call_order == ["stage_one", "stage_two"]
        assert len(results) == 2
        assert all(r.gate_passed for r in results)


# ---------------------------------------------------------------------------
# Pre-built pipelines
# ---------------------------------------------------------------------------

class TestPrebuiltPipelines:
    EXPECTED_PIPELINES = {
        "full_product",
        "content_machine",
        "startup_launch",
        "full_stack_app",
        "research_to_publish",
    }

    def test_all_prebuilt_pipelines_load(self) -> None:
        pipelines = list_pipelines()
        names = {p.name for p in pipelines}
        missing = self.EXPECTED_PIPELINES - names
        assert not missing, f"Missing pre-built pipelines: {missing}"

    def test_each_pipeline_has_at_least_two_stages(self) -> None:
        for pipeline in list_pipelines():
            assert len(pipeline.stages) >= 2, (
                f"Pipeline '{pipeline.name}' has fewer than 2 stages"
            )

    def test_each_pipeline_has_description(self) -> None:
        for pipeline in list_pipelines():
            assert pipeline.description, (
                f"Pipeline '{pipeline.name}' has no description"
            )

    def test_full_product_stage_names(self) -> None:
        p = get_pipeline("full_product")
        names = [s.template_name for s in p.stages]
        assert "market_research" in names
        assert "product_spec" in names
        assert "web_app" in names
        assert "codebase_audit" in names
        assert "course_creator" in names

    def test_content_machine_stage_names(self) -> None:
        p = get_pipeline("content_machine")
        names = [s.template_name for s in p.stages]
        assert "seo_article" in names
        assert "social_media_campaign" in names
        assert "newsletter" in names

    def test_startup_launch_stage_names(self) -> None:
        p = get_pipeline("startup_launch")
        names = [s.template_name for s in p.stages]
        assert "market_research" in names
        assert "startup_pitch" in names
        assert "financial_model" in names
        assert "legal_review" in names

    def test_full_stack_app_stage_names(self) -> None:
        p = get_pipeline("full_stack_app")
        names = [s.template_name for s in p.stages]
        assert "product_spec" in names
        assert "api_service" in names
        assert "web_app" in names
        assert "mobile_app" in names
        assert "monitoring_setup" in names

    def test_research_to_publish_stage_names(self) -> None:
        p = get_pipeline("research_to_publish")
        names = [s.template_name for s in p.stages]
        assert "market_research" in names
        assert "academic_paper" in names
        assert "course_creator" in names

    def test_get_pipeline_unknown_raises(self) -> None:
        with pytest.raises(KeyError, match="not found"):
            get_pipeline("nonexistent_pipeline")

    def test_full_product_has_debate_gates(self) -> None:
        p = get_pipeline("full_product")
        gate_stages = [s for s in p.stages if s.debate_gate]
        assert len(gate_stages) >= 2, (
            "full_product should have at least 2 debate gates"
        )

    def test_startup_launch_has_debate_gates(self) -> None:
        p = get_pipeline("startup_launch")
        gate_stages = [s for s in p.stages if s.debate_gate]
        assert len(gate_stages) >= 2, (
            "startup_launch should have at least 2 debate gates"
        )
