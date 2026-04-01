"""Codebase analysis agent — actually reads a git repo."""

from __future__ import annotations

import os
import stat
from collections import defaultdict
from pathlib import Path
from typing import Any

from ..core.agent import AgentResult, BaseAgent
from ..core.state import ScanResult

SKIP_DIRS = {
    ".git", "node_modules", "__pycache__", ".venv", "venv", "env",
    ".env", "dist", "build", ".next", ".nuxt", "coverage", ".cache",
    "vendor", "target", ".mypy_cache", ".pytest_cache", ".ruff_cache",
}

EXT_TO_LANG: dict[str, str] = {
    ".py": "Python", ".ts": "TypeScript", ".tsx": "TypeScript",
    ".js": "JavaScript", ".jsx": "JavaScript", ".go": "Go",
    ".rs": "Rust", ".java": "Java", ".kt": "Kotlin",
    ".rb": "Ruby", ".php": "PHP", ".cs": "C#",
    ".cpp": "C++", ".c": "C", ".h": "C/C++",
    ".swift": "Swift", ".ex": "Elixir", ".exs": "Elixir",
    ".hs": "Haskell", ".ml": "OCaml", ".scala": "Scala",
    ".sh": "Shell", ".bash": "Shell", ".zsh": "Shell",
    ".html": "HTML", ".css": "CSS", ".scss": "SCSS",
    ".json": "JSON", ".yaml": "YAML", ".yml": "YAML",
    ".toml": "TOML", ".md": "Markdown", ".sql": "SQL",
}


class ScannerAgent(BaseAgent):
    """
    Analyzes a git repository: languages, structure, dependencies, git stats.
    Works on real repos — no stubs.
    """

    name = "scanner"

    @property
    def system_prompt(self) -> str:
        return (
            "You are a senior software architect with deep expertise in codebase analysis. "
            "You synthesize raw repository statistics into actionable insights. "
            "Be specific, technical, and evidence-based. Identify strengths, risks, and patterns."
        )

    async def run(self, repo_path: str, **_: Any) -> AgentResult:
        path = Path(repo_path).expanduser().resolve()
        if not path.exists():
            return AgentResult(
                agent_name=self.name,
                success=False,
                output=None,
                error=f"Path does not exist: {path}",
            )

        languages: dict[str, int] = defaultdict(int)
        file_count = 0
        total_lines = 0
        structure: dict[str, Any] = {}
        dependencies: list[str] = []

        # Walk the filesystem
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS and not d.startswith(".")]
            rel_root = Path(root).relative_to(path)
            depth = len(rel_root.parts)
            if depth > 6:
                dirs.clear()
                continue

            for fname in files:
                fpath = Path(root) / fname
                ext = fpath.suffix.lower()
                lang = EXT_TO_LANG.get(ext)

                # Count lines for source files
                if lang and lang not in ("JSON", "YAML", "TOML", "Markdown"):
                    try:
                        lines = self._count_lines(fpath)
                        languages[lang] += lines
                        total_lines += lines
                        file_count += 1
                    except OSError:
                        pass
                elif lang:
                    file_count += 1

            # Capture top-level structure (depth 0 and 1)
            if depth == 0:
                structure["root_files"] = [f for f in files if not f.startswith(".")]
                structure["root_dirs"] = [d for d in dirs]

        # Detect dependency files
        dep_files = {
            "requirements.txt": "pip",
            "pyproject.toml": "pip/hatch",
            "package.json": "npm/yarn/pnpm",
            "Cargo.toml": "cargo",
            "go.mod": "go modules",
            "Gemfile": "bundler",
            "pom.xml": "maven",
            "build.gradle": "gradle",
            "composer.json": "composer",
        }
        for dep_file, manager in dep_files.items():
            if (path / dep_file).exists():
                dependencies.append(f"{dep_file} ({manager})")

        # Git statistics
        git_stats = self._read_git_stats(path)

        # Sort languages by line count
        sorted_langs = dict(sorted(languages.items(), key=lambda x: -x[1]))

        # Synthesize a summary via LLM
        summary = await self._synthesize_summary(
            repo_path=str(path),
            languages=sorted_langs,
            file_count=file_count,
            total_lines=total_lines,
            dependencies=dependencies,
            structure=structure,
            git_stats=git_stats,
        )

        result = ScanResult(
            repo_path=str(path),
            languages=sorted_langs,
            file_count=file_count,
            total_lines=total_lines,
            dependencies=dependencies,
            structure=structure,
            git_stats=git_stats,
            summary=summary,
        )

        await self._state.set_typed("scan", result)

        return AgentResult(
            agent_name=self.name,
            success=True,
            output=result.model_dump(),
        )

    def _count_lines(self, path: Path) -> int:
        try:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return sum(1 for _ in f)
        except (OSError, PermissionError):
            return 0

    def _read_git_stats(self, repo_path: Path) -> dict[str, Any]:
        git_dir = repo_path / ".git"
        if not git_dir.exists():
            return {"is_git_repo": False}

        stats: dict[str, Any] = {"is_git_repo": True}
        try:
            import git  # type: ignore[import]
            repo = git.Repo(repo_path)
            try:
                stats["branch"] = repo.active_branch.name
            except TypeError:
                stats["branch"] = "detached HEAD"

            commits = list(repo.iter_commits(max_count=100))
            stats["total_commits_sample"] = len(commits)

            if commits:
                stats["latest_commit"] = {
                    "sha": commits[0].hexsha[:8],
                    "message": commits[0].message.strip()[:100],
                    "author": str(commits[0].author),
                    "date": commits[0].committed_datetime.isoformat(),
                }
                authors: dict[str, int] = defaultdict(int)
                for c in commits:
                    authors[str(c.author)] += 1
                stats["top_contributors"] = sorted(
                    authors.items(), key=lambda x: -x[1]
                )[:5]

        except Exception as exc:  # gitpython not installed or not a valid repo
            stats["git_error"] = str(exc)

        return stats

    async def _synthesize_summary(self, **kwargs: Any) -> str:
        lang_summary = ", ".join(
            f"{lang} ({lines:,} lines)"
            for lang, lines in list(kwargs["languages"].items())[:5]
        )
        prompt = f"""Analyze this repository and write a concise technical summary (3-5 sentences).

Repository: {kwargs["repo_path"]}
Files: {kwargs["file_count"]:,} source files
Total Lines: {kwargs["total_lines"]:,}
Languages: {lang_summary or "unknown"}
Dependencies: {", ".join(kwargs["dependencies"]) or "none detected"}
Git: {kwargs["git_stats"].get("total_commits_sample", "N/A")} commits sampled, branch: {kwargs["git_stats"].get("branch", "N/A")}
Top-level structure: dirs={kwargs["structure"].get("root_dirs", [])[:8]}, files={kwargs["structure"].get("root_files", [])[:8]}

Focus on: tech stack assessment, apparent purpose, code health indicators, and notable structural patterns."""

        return await self._llm([{"role": "user", "content": prompt}])
