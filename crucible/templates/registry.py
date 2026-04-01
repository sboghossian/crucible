"""Template registry — discovers and loads all catalog templates."""

from __future__ import annotations

import importlib
import pkgutil
from pathlib import Path
from typing import Any

from .base import Template, TemplateSession, _REGISTRY


class TemplateRegistry:
    """
    Discovers and loads templates from the catalog package.

    Templates are auto-discovered: any module in ``crucible/templates/catalog/``
    that calls ``template(...)`` at import time is automatically registered.
    """

    def __init__(self) -> None:
        self._loaded = False

    def _ensure_loaded(self) -> None:
        if self._loaded:
            return
        catalog_path = Path(__file__).parent / "catalog"
        for finder, module_name, _ in pkgutil.iter_modules([str(catalog_path)]):
            importlib.import_module(
                f"crucible.templates.catalog.{module_name}"
            )
        self._loaded = True

    def list_templates(self) -> list[Template]:
        """Return all registered templates, sorted by category then name."""
        self._ensure_loaded()
        return sorted(_REGISTRY.values(), key=lambda t: (t.category, t.name))

    def get_template(self, name: str) -> Template:
        """Return a template by name, raising KeyError if not found."""
        self._ensure_loaded()
        if name not in _REGISTRY:
            available = sorted(_REGISTRY.keys())
            raise KeyError(
                f"Template '{name}' not found.\n"
                f"Available ({len(available)}): {', '.join(available)}"
            )
        return _REGISTRY[name]

    def list_categories(self) -> dict[str, list[Template]]:
        """Return templates grouped by category."""
        self._ensure_loaded()
        categories: dict[str, list[Template]] = {}
        for t in self.list_templates():
            categories.setdefault(t.category, []).append(t)
        return dict(sorted(categories.items()))

    def search(self, query: str) -> list[Template]:
        """Full-text search across name, description, and tags."""
        self._ensure_loaded()
        q = query.lower()
        return [
            t for t in self.list_templates()
            if q in t.name.lower()
            or q in t.description.lower()
            or any(q in tag.lower() for tag in t.tags)
        ]

    def deploy_template(
        self,
        name: str,
        api_key: str | None = None,
        model: str | None = None,
        **kwargs: Any,
    ) -> TemplateSession:
        """
        Create a TemplateSession ready to run the named template.

        ``kwargs`` are stored and forwarded to ``TemplateSession.run()``.
        """
        tmpl = self.get_template(name)
        return TemplateSession(template=tmpl, api_key=api_key, model=model)


# Module-level singleton
registry = TemplateRegistry()
