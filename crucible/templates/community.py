"""Community template registry — discover, validate, and install user-submitted templates."""

from __future__ import annotations

import importlib.util
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import logging

from .base import Template, _REGISTRY

logger = logging.getLogger(__name__)

# Default community templates directory (shipped alongside the package)
_DEFAULT_COMMUNITY_DIR = Path(__file__).parent / "community_templates"

# Local install target — community templates installed by the user live here
_INSTALLED_DIR = _DEFAULT_COMMUNITY_DIR / "installed"


@dataclass
class TemplateSubmission:
    """Metadata for a community-submitted template."""

    name: str
    author: str
    description: str
    version: str
    license: str
    tags: list[str] = field(default_factory=list)
    tested_with_crucible_version: str = ""
    source_path: str = ""


class ValidationError(Exception):
    """Raised when a community template fails quality gates."""


def validate_submission(path: str | Path) -> TemplateSubmission:
    """Run quality gates on a community template module.

    The module must expose a module-level ``SUBMISSION`` attribute of type
    ``TemplateSubmission`` and a ``TEMPLATE`` attribute of type ``Template``.

    Quality gates (all must pass):
    - ``SUBMISSION`` present with non-empty author and description
    - ``TEMPLATE`` present with at least 2 agents
    - At least 1 debate topic defined
    - At least 1 expected output defined

    Returns the ``TemplateSubmission`` on success; raises ``ValidationError`` on failure.
    """
    p = Path(path)
    if not p.exists():
        raise ValidationError(f"Path does not exist: {p}")

    # Support both single .py files and package directories (with __init__.py)
    if p.is_dir():
        module_file = p / "__init__.py"
        if not module_file.exists():
            raise ValidationError(f"Directory template must have __init__.py: {p}")
    elif p.suffix == ".py":
        module_file = p
    else:
        raise ValidationError(f"Expected a .py file or a directory: {p}")

    spec = importlib.util.spec_from_file_location("_community_validate_tmp", module_file)
    if spec is None or spec.loader is None:
        raise ValidationError(f"Could not load module from: {module_file}")

    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)  # type: ignore[union-attr]
    except Exception as exc:
        raise ValidationError(f"Error executing module {module_file}: {exc}") from exc

    submission: Any = getattr(module, "SUBMISSION", None)
    tmpl: Any = getattr(module, "TEMPLATE", None)

    errors: list[str] = []

    if submission is None:
        errors.append("Missing module-level SUBMISSION attribute (TemplateSubmission instance)")
    else:
        if not isinstance(submission, TemplateSubmission):
            errors.append("SUBMISSION must be a TemplateSubmission instance")
        else:
            if not submission.author:
                errors.append("SUBMISSION.author must not be empty")
            if not submission.description:
                errors.append("SUBMISSION.description must not be empty")

    if tmpl is None:
        errors.append("Missing module-level TEMPLATE attribute (Template instance)")
    else:
        if not isinstance(tmpl, Template):
            errors.append("TEMPLATE must be a Template instance")
        else:
            if len(tmpl.agents) < 2:
                errors.append(
                    f"Template must have at least 2 agents, found {len(tmpl.agents)}"
                )
            if not tmpl.debate_topics:
                errors.append("Template must define at least 1 debate topic")
            if not tmpl.expected_outputs:
                errors.append("Template must define at least 1 expected output")
            if not tmpl.description:
                errors.append("Template must have a description")

    if errors:
        raise ValidationError(
            "Template failed quality gates:\n" + "\n".join(f"  • {e}" for e in errors)
        )

    assert isinstance(submission, TemplateSubmission)
    submission.source_path = str(p.resolve())
    return submission


def install_template(source: str | Path) -> str:
    """Validate and copy a community template into the local installed directory.

    Returns the installed template's name.

    Raises ``ValidationError`` if quality gates fail.
    Raises ``FileExistsError`` if a template with the same name is already installed.
    """
    source = Path(source)
    submission = validate_submission(source)

    _INSTALLED_DIR.mkdir(parents=True, exist_ok=True)

    if source.is_dir():
        dest = _INSTALLED_DIR / source.name
        if dest.exists():
            raise FileExistsError(
                f"Community template '{source.name}' is already installed at {dest}. "
                "Remove it first to reinstall."
            )
        shutil.copytree(source, dest)
        logger.info("Installed community template directory '%s' → %s", source.name, dest)
    else:
        dest = _INSTALLED_DIR / source.name
        if dest.exists():
            raise FileExistsError(
                f"Community template '{source.name}' is already installed at {dest}. "
                "Remove it first to reinstall."
            )
        shutil.copy2(source, dest)
        logger.info("Installed community template file '%s' → %s", source.name, dest)

    # Load the newly installed template so it registers in _REGISTRY
    _load_community_file(dest)
    return submission.name or dest.stem


def list_community_templates() -> list[dict[str, Any]]:
    """Return metadata for all installed community templates.

    Each entry is a dict with keys: name, author, description, version, license,
    tags, tested_with_crucible_version, source_path, registered (bool).
    """
    if not _INSTALLED_DIR.exists():
        return []

    results: list[dict[str, Any]] = []
    for item in sorted(_INSTALLED_DIR.iterdir()):
        if item.is_dir():
            module_file = item / "__init__.py"
        elif item.suffix == ".py" and item.stem != "__init__":
            module_file = item
        else:
            continue

        try:
            submission = validate_submission(item if item.is_dir() else item)
            results.append({
                "name": submission.name,
                "author": submission.author,
                "description": submission.description,
                "version": submission.version,
                "license": submission.license,
                "tags": submission.tags,
                "tested_with_crucible_version": submission.tested_with_crucible_version,
                "source_path": str(item),
                "registered": submission.name in _REGISTRY,
            })
        except ValidationError as exc:
            logger.warning("Skipping invalid community template at %s: %s", item, exc)

    return results


class CommunityRegistry:
    """Discovers and loads community templates from a directory.

    Community templates live separately from the built-in catalog.
    On first access they are loaded and registered alongside built-in templates,
    but they appear distinctly in ``list_community_templates()``.
    """

    def __init__(self, community_dir: str | Path | None = None) -> None:
        self._dir = Path(community_dir) if community_dir else _INSTALLED_DIR
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        if not self._dir.exists():
            self._loaded = True
            return
        for item in sorted(self._dir.iterdir()):
            if item.is_dir():
                module_file = item / "__init__.py"
            elif item.suffix == ".py" and item.stem != "__init__":
                module_file = item
            else:
                continue
            try:
                _load_community_file(module_file)
            except Exception as exc:
                logger.warning("Could not load community template %s: %s", item, exc)
        self._loaded = True

    def list(self) -> list[dict[str, Any]]:
        """Return all installed community templates as metadata dicts."""
        self._ensure_loaded()
        return list_community_templates()

    def get(self, name: str) -> Template:
        """Return a community template by name (must be registered)."""
        self._ensure_loaded()
        if name not in _REGISTRY:
            raise KeyError(f"Community template '{name}' not found or not loaded.")
        return _REGISTRY[name]


def _load_community_file(path: Path) -> None:
    """Import a community module and register its TEMPLATE if present."""
    spec = importlib.util.spec_from_file_location(f"_community_{path.stem}", path)
    if spec is None or spec.loader is None:
        return
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    tmpl: Any = getattr(module, "TEMPLATE", None)
    if tmpl is not None and isinstance(tmpl, Template):
        _REGISTRY[tmpl.name] = tmpl
        logger.info("Registered community template '%s'", tmpl.name)


# Module-level singleton
community_registry = CommunityRegistry()
