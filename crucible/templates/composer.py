"""Template Composer — combine templates into multi-stage pipelines."""

from __future__ import annotations

import asyncio
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn

logger = logging.getLogger(__name__)
console = Console()

# Imported lazily to avoid circular imports at collection time; resolved on first use.
# Tests can patch `crucible.templates.composer._get_registry` to inject fakes.
def _get_registry() -> Any:
    from .registry import registry as _registry
    return _registry


@dataclass
class PipelineStage:
    """
    A single stage in a pipeline, wrapping a template with optional I/O mappings.

    ``input_keys``: keys to extract from the previous stage's outputs and pass
                    as additional context to this stage's agents.
    ``output_keys``: keys (agent names) whose outputs are forwarded downstream.
                     If empty, all agent outputs are forwarded.
    ``debate_gate``: if True, run a Debate Council after this stage to decide
                     whether the pipeline should continue.
    ``gate_topic``:  the question the Debate Council answers (default is generic).
    """

    template_name: str
    input_keys: list[str] = field(default_factory=list)
    output_keys: list[str] = field(default_factory=list)
    debate_gate: bool = False
    gate_topic: str = ""

    def __post_init__(self) -> None:
        if self.debate_gate and not self.gate_topic:
            self.gate_topic = (
                f"Should the pipeline continue after the '{self.template_name}' stage?"
            )


@dataclass
class StageResult:
    """Outcome of a single pipeline stage execution."""

    stage_index: int
    template_name: str
    outputs: dict[str, Any]
    gate_passed: bool = True
    gate_decision: str = ""
    duration_seconds: float = 0.0
    error: str = ""

    @property
    def success(self) -> bool:
        return not self.error

    def context_for_next_stage(self, output_keys: list[str]) -> str:
        """Build a context string to inject into the next stage."""
        relevant = (
            {k: v for k, v in self.outputs.items() if k in output_keys}
            if output_keys
            else {k: v for k, v in self.outputs.items() if not k.startswith("_")}
        )
        parts = [f"=== Output from '{self.template_name}' stage ==="]
        for agent_name, data in relevant.items():
            output_text = str(data.get("output", "")) if isinstance(data, dict) else str(data)
            if output_text:
                parts.append(f"\n[{agent_name}]:\n{output_text[:1200]}")
        return "\n".join(parts)


class Pipeline:
    """
    An ordered sequence of template stages with data flow between them.

    Data flow: the outputs of stage N are summarised and injected as context
    into stage N+1.  An optional Debate Council gate after each stage can halt
    the pipeline early.
    """

    def __init__(
        self,
        name: str,
        stages: list[PipelineStage],
        description: str = "",
    ) -> None:
        if not stages:
            raise ValueError("Pipeline must have at least one stage.")
        self.name = name
        self.description = description
        self.stages = stages

    async def run(
        self,
        subject: str,
        api_key: str | None = None,
        model: str = "claude-opus-4-6",
        verbose: bool = False,
        on_stage_start: Callable[[int, str], None] | None = None,
        on_stage_end: Callable[[int, StageResult], None] | None = None,
    ) -> list[StageResult]:
        """
        Execute every stage in order, threading outputs forward as context.

        Returns a list of StageResult, one per stage executed (may be shorter
        than ``self.stages`` if a debate gate stops the pipeline).
        """
        import anthropic

        client = anthropic.AsyncAnthropic(api_key=api_key)
        run_id = str(uuid.uuid4())

        results: list[StageResult] = []
        accumulated_context = ""

        for idx, stage in enumerate(self.stages):
            if on_stage_start:
                on_stage_start(idx, stage.template_name)

            t_start = datetime.utcnow()

            # ---- build extra kwargs from previous stage context ----
            extra_kwargs: dict[str, Any] = {}
            if accumulated_context:
                extra_kwargs["context"] = accumulated_context

            # ---- run the template session ----
            try:
                session = _get_registry().deploy_template(
                    stage.template_name,
                    api_key=api_key,
                    model=model,
                )
                stage_outputs = await session.run(subject=subject, **extra_kwargs)
            except Exception as exc:
                logger.error("Stage %d (%s) failed: %s", idx, stage.template_name, exc)
                sr = StageResult(
                    stage_index=idx,
                    template_name=stage.template_name,
                    outputs={},
                    error=str(exc),
                    duration_seconds=(datetime.utcnow() - t_start).total_seconds(),
                )
                results.append(sr)
                if on_stage_end:
                    on_stage_end(idx, sr)
                break

            duration = (datetime.utcnow() - t_start).total_seconds()

            sr = StageResult(
                stage_index=idx,
                template_name=stage.template_name,
                outputs=stage_outputs,
                duration_seconds=duration,
            )

            # ---- debate gate ----
            if stage.debate_gate:
                gate_passed, gate_decision = await _run_debate_gate(
                    client=client,
                    model=model,
                    topic=stage.gate_topic,
                    stage_result=sr,
                    subject=subject,
                )
                sr.gate_passed = gate_passed
                sr.gate_decision = gate_decision

            results.append(sr)
            if on_stage_end:
                on_stage_end(idx, sr)

            if not sr.gate_passed:
                logger.info(
                    "Pipeline '%s' halted after stage %d by debate gate.", self.name, idx
                )
                break

            # ---- thread context forward ----
            accumulated_context = sr.context_for_next_stage(stage.output_keys)

        return results


async def _run_debate_gate(
    client: Any,
    model: str,
    topic: str,
    stage_result: StageResult,
    subject: str,
) -> tuple[bool, str]:
    """
    Run a Debate Council to decide whether the pipeline should proceed.

    Returns (gate_passed, decision_text).
    """
    from ..core.agent import AgentConfig
    from ..core.events import EventBus
    from ..core.state import SharedState

    try:
        from ..agents.debate_council import DebateCouncilAgent

        run_id = str(uuid.uuid4())
        state = SharedState(run_id=run_id, subject=subject)
        bus = EventBus()
        dc = DebateCouncilAgent(
            client=client,
            state=state,
            bus=bus,
            config=AgentConfig(model=model),
        )
        summary = stage_result.context_for_next_stage([])[:2000]
        debate_result = await dc.execute(
            topic=topic,
            options=["proceed", "halt"],
            context=(
                f"Subject: {subject}\nStage: {stage_result.template_name}\n\n{summary}"
            ),
        )
        decision_text = str(debate_result.output or "")
        gate_passed = "halt" not in decision_text.lower()
        return gate_passed, decision_text
    except Exception as exc:
        logger.warning("Debate gate failed, defaulting to proceed: %s", exc)
        return True, f"Gate skipped (error: {exc})"


class PipelineBuilder:
    """
    Fluent API for composing pipelines.

    Example::

        pipeline = (
            PipelineBuilder("my_pipeline")
            .then("market_research")
            .then("product_spec", debate_gate=True)
            .then("web_app")
            .build()
        )
    """

    def __init__(self, name: str, description: str = "") -> None:
        self._name = name
        self._description = description
        self._stages: list[PipelineStage] = []

    def then(
        self,
        template_name: str,
        *,
        input_keys: list[str] | None = None,
        output_keys: list[str] | None = None,
        debate_gate: bool = False,
        gate_topic: str = "",
    ) -> "PipelineBuilder":
        self._stages.append(
            PipelineStage(
                template_name=template_name,
                input_keys=input_keys or [],
                output_keys=output_keys or [],
                debate_gate=debate_gate,
                gate_topic=gate_topic,
            )
        )
        return self

    def build(self) -> Pipeline:
        return Pipeline(
            name=self._name,
            description=self._description,
            stages=self._stages,
        )


# ---------------------------------------------------------------------------
# Rich CLI helper — used by __main__.py
# ---------------------------------------------------------------------------

async def run_pipeline_cli(
    pipeline: Pipeline,
    subject: str,
    api_key: str | None,
    model: str,
    verbose: bool = False,
) -> list[StageResult]:
    """Run a pipeline with Rich progress output."""
    total = len(pipeline.stages)

    console.print()
    console.print(Panel(
        f"[bold cyan]{pipeline.name}[/bold cyan]\n"
        f"[dim]{pipeline.description}[/dim]\n\n"
        f"Subject: [yellow]{subject}[/yellow]  |  "
        f"Stages: [green]{total}[/green]",
        title="Pipeline",
    ))

    stage_names = [s.template_name for s in pipeline.stages]
    console.print(
        "  " + "  →  ".join(f"[cyan]{n}[/cyan]" for n in stage_names)
    )
    console.print()

    current_spinner: list[Any] = []

    def on_start(idx: int, name: str) -> None:
        console.print(
            f"[bold white][{idx + 1}/{total}][/bold white] "
            f"Running [cyan]{name}[/cyan]…"
        )
        if idx > 0:
            console.print(
                f"  [dim]Context from previous stage will be injected[/dim]"
            )

    def on_end(idx: int, sr: StageResult) -> None:
        icon = "[green]✓[/green]" if sr.success else "[red]✗[/red]"
        dur = f"  [dim]{sr.duration_seconds:.1f}s[/dim]"
        console.print(f"  {icon} [bold]{sr.template_name}[/bold] complete{dur}")

        if sr.gate_decision:
            gate_icon = "[green]▶ proceed[/green]" if sr.gate_passed else "[red]■ halt[/red]"
            console.print(f"  Debate gate → {gate_icon}")
            if verbose:
                console.print(f"  [dim]{sr.gate_decision[:400]}[/dim]")

        if sr.error:
            console.print(f"  [red]Error: {sr.error}[/red]")

        if verbose and sr.success:
            for agent_name, data in sr.outputs.items():
                if agent_name.startswith("_"):
                    continue
                output = str(data.get("output", "")) if isinstance(data, dict) else ""
                if output:
                    console.print(
                        f"\n  [bold]{agent_name}:[/bold]\n"
                        + "\n".join(f"  {line}" for line in output[:600].splitlines())
                    )
        console.print()

    results = await pipeline.run(
        subject=subject,
        api_key=api_key,
        model=model,
        verbose=verbose,
        on_stage_start=on_start,
        on_stage_end=on_end,
    )

    completed = sum(1 for r in results if r.success)
    halted_early = len(results) < total

    summary_lines = [
        f"[bold green]Pipeline complete[/bold green]" if not halted_early
        else "[bold yellow]Pipeline halted early by debate gate[/bold yellow]",
        f"Stages run: {len(results)}/{total}  |  Successful: {completed}",
    ]
    if halted_early:
        summary_lines.append(
            f"Halted after: [cyan]{results[-1].template_name}[/cyan]"
        )

    console.print(Panel("\n".join(summary_lines), title="Done"))
    return results
