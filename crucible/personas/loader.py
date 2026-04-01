"""Load persona definitions from YAML or JSON files."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from ..debate.personas import Persona
from .schema import PersonaConfig
from .validator import validate_persona_dict

logger = logging.getLogger(__name__)


def _parse_file(path: Path) -> dict[str, Any]:
    """Parse a single YAML or JSON file into a raw dict."""
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        try:
            import yaml  # type: ignore[import-untyped]
        except ImportError as exc:
            raise ImportError(
                "PyYAML is required to load YAML persona files: pip install pyyaml"
            ) from exc
        with path.open("r", encoding="utf-8") as fh:
            return yaml.safe_load(fh) or {}
    elif suffix == ".json":
        with path.open("r", encoding="utf-8") as fh:
            return json.load(fh)
    else:
        raise ValueError(f"Unsupported persona file format: {path.suffix!r} ({path})")


def config_to_persona(config: PersonaConfig) -> Persona:
    """Convert a validated PersonaConfig into the core Persona dataclass."""
    return Persona(
        name=config.name,
        role=config.role,
        system_prompt=config.system_prompt,
        scoring_weight=config.scoring_weights.as_dict(),
    )


def load_persona_file(path: Path | str) -> Persona:
    """Load and validate a single persona file, returning a Persona."""
    path = Path(path)
    raw = _parse_file(path)
    config = validate_persona_dict(raw)
    persona = config_to_persona(config)
    logger.debug("Loaded persona %r from %s", persona.name, path)
    return persona


def load_personas_dir(directory: Path | str) -> list[Persona]:
    """
    Load all YAML/JSON persona files from *directory*.

    Files that fail validation are skipped with a warning.
    Returns personas sorted by name for deterministic ordering.
    """
    directory = Path(directory)
    if not directory.is_dir():
        raise NotADirectoryError(f"Personas directory not found: {directory}")

    personas: list[Persona] = []
    for path in sorted(directory.iterdir()):
        if path.suffix.lower() not in {".yaml", ".yml", ".json"}:
            continue
        try:
            personas.append(load_persona_file(path))
        except (ValueError, KeyError) as exc:
            logger.warning("Skipping %s: %s", path.name, exc)

    logger.info("Loaded %d persona(s) from %s", len(personas), directory)
    return personas


def filter_personas(
    personas: list[Persona], names: list[str]
) -> list[Persona]:
    """Return only the personas whose names match *names* (case-insensitive slugs)."""
    normalised = {n.strip().lower().replace(" ", "_").replace("-", "_") for n in names}
    selected = [p for p in personas if p.name in normalised]
    missing = normalised - {p.name for p in selected}
    if missing:
        available = [p.name for p in personas]
        raise ValueError(
            f"Unknown persona(s): {sorted(missing)}. Available: {available}"
        )
    return selected
