"""Template versioning — semver parsing, comparison, and compatibility."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import Template


@dataclass(order=True)
class TemplateVersion:
    """Semantic version with comparison operators."""

    major: int
    minor: int
    patch: int

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"

    def __repr__(self) -> str:
        return f"TemplateVersion({self.major}, {self.minor}, {self.patch})"


def version_from_string(version_str: str) -> TemplateVersion:
    """Parse a semver string like '1.2.3' into a TemplateVersion.

    Raises ValueError for invalid inputs.
    """
    parts = version_str.strip().split(".")
    if len(parts) != 3:
        raise ValueError(
            f"Invalid version string '{version_str}': expected 'major.minor.patch'"
        )
    try:
        major, minor, patch = int(parts[0]), int(parts[1]), int(parts[2])
    except ValueError:
        raise ValueError(
            f"Invalid version string '{version_str}': components must be integers"
        )
    if major < 0 or minor < 0 or patch < 0:
        raise ValueError(
            f"Invalid version string '{version_str}': components must be non-negative"
        )
    return TemplateVersion(major=major, minor=minor, patch=patch)


def is_compatible(required: TemplateVersion, available: TemplateVersion) -> bool:
    """Return True if *available* satisfies *required* under semver rules.

    Compatibility rules:
    - Major versions must match (breaking changes).
    - Available minor must be >= required minor (new features are backwards-compatible).
    - If minor versions are equal, available patch must be >= required patch.
    """
    if available.major != required.major:
        return False
    if available.minor > required.minor:
        return True
    if available.minor == required.minor:
        return available.patch >= required.patch
    return False


@dataclass
class VersionedTemplate:
    """A Template wrapped with version history and author metadata."""

    template: "Template"
    author: str = ""
    license: str = "MIT"
    changelog: list[tuple[str, str]] = field(default_factory=list)
    """List of (version_string, change_description) entries, newest first."""

    @property
    def version(self) -> TemplateVersion:
        return version_from_string(self.template.version)

    def add_changelog_entry(self, version: str, description: str) -> None:
        self.changelog.insert(0, (version, description))

    def latest_changes(self) -> str | None:
        """Return the description of the most recent changelog entry, or None."""
        if self.changelog:
            return self.changelog[0][1]
        return None
