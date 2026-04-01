"""Pre-built multi-stage pipelines."""

from __future__ import annotations

from ..composer import Pipeline, PipelineBuilder

# Registry of pre-built pipelines keyed by slug name
_PIPELINES: dict[str, Pipeline] = {}


def _register(pipeline: Pipeline) -> Pipeline:
    _PIPELINES[pipeline.name] = pipeline
    return pipeline


def get_pipeline(name: str) -> Pipeline:
    _ensure_loaded()
    if name not in _PIPELINES:
        available = sorted(_PIPELINES.keys())
        raise KeyError(
            f"Pipeline '{name}' not found.\n"
            f"Available ({len(available)}): {', '.join(available)}"
        )
    return _PIPELINES[name]


def list_pipelines() -> list[Pipeline]:
    _ensure_loaded()
    return sorted(_PIPELINES.values(), key=lambda p: p.name)


_loaded = False


def _ensure_loaded() -> None:
    global _loaded
    if _loaded:
        return
    from . import (  # noqa: F401
        full_product,
        content_machine,
        startup_launch,
        full_stack_app,
        research_to_publish,
    )
    _loaded = True
