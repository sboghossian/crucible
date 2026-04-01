"""Validation helpers for persona configuration dicts."""

from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from .schema import PersonaConfig


def validate_persona_dict(data: dict[str, Any]) -> PersonaConfig:
    """
    Validate a raw dict (from YAML/JSON) against the PersonaConfig schema.

    Raises ``ValueError`` with a human-readable message on failure.
    """
    try:
        return PersonaConfig.model_validate(data)
    except ValidationError as exc:
        errors = "; ".join(
            f"{'.'.join(str(loc) for loc in e['loc'])}: {e['msg']}"
            for e in exc.errors()
        )
        raise ValueError(f"Invalid persona config: {errors}") from exc
