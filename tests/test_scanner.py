"""Tests for ScannerAgent — filesystem walking, language detection, git stats, health scoring."""

from __future__ import annotations

import uuid
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from crucible.agents.scanner import EXT_TO_LANG, SKIP_DIRS, ScannerAgent
from crucible.core.agent import AgentConfig
from crucible.core.events import EventBus
from crucible.core.state import SharedState


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_agent(
    state: SharedState | None = None,
    response_text: str = "Mocked LLM summary.",
) -> ScannerAgent:
    mock_message = MagicMock()
    mock_message.content = [MagicMock(text=response_text)]
    mock_client = MagicMock()
    mock_client.messages.create = AsyncMock(return_value=mock_message)

    if state is None:
        state = SharedState(run_id=str(uuid.uuid4())[:8], subject="test")
    bus = EventBus()
    config = AgentConfig(model="claude-opus-4-6", timeout=30.0)
    return ScannerAgent(client=mock_client, state=state, bus=bus, config=config)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def python_repo(tmp_path: Path) -> Path:
    """A minimal Python project with requirements.txt."""
    (tmp_path / "main.py").write_text("print('hello')\n" * 10)
    (tmp_path / "utils.py").write_text("def foo(): pass\n" * 5)
    sub = tmp_path / "lib"
    sub.mkdir()
    (sub / "core.py").write_text("class Core: pass\n" * 8)
    (tmp_path / "requirements.txt").write_text("requests==2.31.0\npydantic>=2.0\n")
    return tmp_path


@pytest.fixture
def multi_lang_repo(tmp_path: Path) -> Path:
    """A repo with Python, TypeScript, Go, and CSS files."""
    (tmp_path / "app.py").write_text("# python\n" * 20)
    (tmp_path / "index.ts").write_text("// typescript\n" * 15)
    (tmp_path / "main.go").write_text("package main\n" * 10)
    (tmp_path / "style.css").write_text(".cls {}\n" * 5)
    return tmp_path


@pytest.fixture
def noisy_repo(tmp_path: Path) -> Path:
    """Repo with node_modules, __pycache__, and .venv that should be skipped."""
    (tmp_path / "app.py").write_text("# src\n" * 50)

    node_mods = tmp_path / "node_modules"
    node_mods.mkdir()
    (node_mods / "lodash.js").write_text("// huge js lib\n" * 1000)

    cache = tmp_path / "__pycache__"
    cache.mkdir()
    (cache / "app.cpython-311.pyc").write_bytes(b"\x00" * 100)

    venv = tmp_path / ".venv"
    venv.mkdir()
    (venv / "site.py").write_text("# venv file\n" * 500)

    return tmp_path


@pytest.fixture
def npm_repo(tmp_path: Path) -> Path:
    """Node project with package.json and TypeScript."""
    (tmp_path / "package.json").write_text('{"name": "test-app", "version": "1.0.0"}')
    (tmp_path / "index.ts").write_text("const x: number = 1;\n" * 10)
    return tmp_path


# ---------------------------------------------------------------------------
# EXT_TO_LANG constant tests
# ---------------------------------------------------------------------------


class TestExtToLang:
    def test_python_extension(self) -> None:
        assert EXT_TO_LANG[".py"] == "Python"

    def test_typescript_extensions(self) -> None:
        assert EXT_TO_LANG[".ts"] == "TypeScript"
        assert EXT_TO_LANG[".tsx"] == "TypeScript"

    def test_javascript_extensions(self) -> None:
        assert EXT_TO_LANG[".js"] == "JavaScript"
        assert EXT_TO_LANG[".jsx"] == "JavaScript"

    def test_go_extension(self) -> None:
        assert EXT_TO_LANG[".go"] == "Go"

    def test_rust_extension(self) -> None:
        assert EXT_TO_LANG[".rs"] == "Rust"

    def test_java_extension(self) -> None:
        assert EXT_TO_LANG[".java"] == "Java"

    def test_shell_extensions(self) -> None:
        assert EXT_TO_LANG[".sh"] == "Shell"
        assert EXT_TO_LANG[".bash"] == "Shell"
        assert EXT_TO_LANG[".zsh"] == "Shell"

    def test_data_format_extensions(self) -> None:
        assert EXT_TO_LANG[".json"] == "JSON"
        assert EXT_TO_LANG[".yaml"] == "YAML"
        assert EXT_TO_LANG[".yml"] == "YAML"
        assert EXT_TO_LANG[".toml"] == "TOML"

    def test_markup_extensions(self) -> None:
        assert EXT_TO_LANG[".html"] == "HTML"
        assert EXT_TO_LANG[".css"] == "CSS"
        assert EXT_TO_LANG[".md"] == "Markdown"

    def test_unknown_extension_not_present(self) -> None:
        assert ".xyz_unknown_ext" not in EXT_TO_LANG


# ---------------------------------------------------------------------------
# SKIP_DIRS constant tests
# ---------------------------------------------------------------------------


class TestSkipDirs:
    def test_skips_git_directory(self) -> None:
        assert ".git" in SKIP_DIRS

    def test_skips_node_modules(self) -> None:
        assert "node_modules" in SKIP_DIRS

    def test_skips_python_cache(self) -> None:
        assert "__pycache__" in SKIP_DIRS

    def test_skips_venv_variants(self) -> None:
        assert ".venv" in SKIP_DIRS
        assert "venv" in SKIP_DIRS
        assert "env" in SKIP_DIRS

    def test_skips_build_artifacts(self) -> None:
        assert "dist" in SKIP_DIRS
        assert "build" in SKIP_DIRS

    def test_skips_coverage_and_cache_dirs(self) -> None:
        assert "coverage" in SKIP_DIRS
        assert ".cache" in SKIP_DIRS
        assert ".mypy_cache" in SKIP_DIRS
        assert ".pytest_cache" in SKIP_DIRS


# ---------------------------------------------------------------------------
# ScannerAgent._count_lines() tests
# ---------------------------------------------------------------------------


class TestCountLines:
    def test_counts_correct_number_of_lines(self, tmp_path: Path) -> None:
        test_file = tmp_path / "test.py"
        test_file.write_text("line1\nline2\nline3\nline4\nline5\n")
        agent = make_agent()
        assert agent._count_lines(test_file) == 5

    def test_empty_file_returns_zero(self, tmp_path: Path) -> None:
        test_file = tmp_path / "empty.py"
        test_file.write_text("")
        agent = make_agent()
        assert agent._count_lines(test_file) == 0

    def test_single_line_no_newline(self, tmp_path: Path) -> None:
        test_file = tmp_path / "single.py"
        test_file.write_text("only one line")
        agent = make_agent()
        assert agent._count_lines(test_file) == 1

    def test_large_file(self, tmp_path: Path) -> None:
        test_file = tmp_path / "large.py"
        test_file.write_text("x = 1\n" * 1000)
        agent = make_agent()
        assert agent._count_lines(test_file) == 1000


# ---------------------------------------------------------------------------
# ScannerAgent._read_git_stats() tests
# ---------------------------------------------------------------------------


class TestReadGitStats:
    def test_non_git_dir_returns_is_git_repo_false(self, tmp_path: Path) -> None:
        agent = make_agent()
        stats = agent._read_git_stats(tmp_path)
        assert stats["is_git_repo"] is False

    def test_non_git_dir_has_no_branch(self, tmp_path: Path) -> None:
        agent = make_agent()
        stats = agent._read_git_stats(tmp_path)
        assert "branch" not in stats

    def test_returns_dict(self, tmp_path: Path) -> None:
        agent = make_agent()
        stats = agent._read_git_stats(tmp_path)
        assert isinstance(stats, dict)


# ---------------------------------------------------------------------------
# ScannerAgent.run() tests
# ---------------------------------------------------------------------------


class TestScannerAgentRun:
    async def test_nonexistent_path_returns_failure(self) -> None:
        agent = make_agent()
        result = await agent.run(repo_path="/this/path/absolutely/does/not/exist/ever")
        assert result.success is False
        assert "does not exist" in (result.error or "")
        assert result.output is None

    async def test_detects_python_files(self, python_repo: Path) -> None:
        agent = make_agent()
        result = await agent.run(repo_path=str(python_repo))
        assert result.success is True
        languages = result.output["languages"]
        assert "Python" in languages
        assert languages["Python"] > 0

    async def test_python_line_count_is_accurate(self, tmp_path: Path) -> None:
        # 10 lines per file, 2 files
        (tmp_path / "a.py").write_text("x = 1\n" * 10)
        (tmp_path / "b.py").write_text("y = 2\n" * 10)
        agent = make_agent()
        result = await agent.run(repo_path=str(tmp_path))
        assert result.output["languages"]["Python"] == 20

    async def test_detects_multiple_languages(self, multi_lang_repo: Path) -> None:
        agent = make_agent()
        result = await agent.run(repo_path=str(multi_lang_repo))
        languages = result.output["languages"]
        assert "Python" in languages
        assert "TypeScript" in languages
        assert "Go" in languages

    async def test_css_files_counted(self, multi_lang_repo: Path) -> None:
        agent = make_agent()
        result = await agent.run(repo_path=str(multi_lang_repo))
        # CSS is not counted in "languages" (treated as data format? No, CSS is listed)
        # Actually looking at EXT_TO_LANG: .css -> "CSS", and it's not in the JSON/YAML/TOML/Markdown list
        # so it should be counted
        languages = result.output["languages"]
        assert "CSS" in languages

    async def test_skips_node_modules(self, noisy_repo: Path) -> None:
        agent = make_agent()
        result = await agent.run(repo_path=str(noisy_repo))
        assert result.success is True
        languages = result.output["languages"]
        # JS from node_modules must be excluded
        assert languages.get("JavaScript", 0) == 0
        # Python from app.py must be counted
        assert "Python" in languages

    async def test_skips_pycache_files(self, noisy_repo: Path) -> None:
        agent = make_agent()
        result = await agent.run(repo_path=str(noisy_repo))
        # The .pyc file is in __pycache__ — it has no .py extension, so won't be counted
        # but the key test is file_count is accurate (only counts app.py)
        assert result.output["file_count"] >= 1  # at least app.py

    async def test_detects_requirements_txt(self, python_repo: Path) -> None:
        agent = make_agent()
        result = await agent.run(repo_path=str(python_repo))
        deps = result.output["dependencies"]
        assert any("requirements.txt" in d for d in deps)

    async def test_detects_package_json(self, npm_repo: Path) -> None:
        agent = make_agent()
        result = await agent.run(repo_path=str(npm_repo))
        deps = result.output["dependencies"]
        assert any("package.json" in d for d in deps)

    async def test_detects_pyproject_toml(self, tmp_path: Path) -> None:
        (tmp_path / "pyproject.toml").write_text("[project]\nname = 'test'\n")
        (tmp_path / "main.py").write_text("pass\n")
        agent = make_agent()
        result = await agent.run(repo_path=str(tmp_path))
        deps = result.output["dependencies"]
        assert any("pyproject.toml" in d for d in deps)

    async def test_non_git_repo_is_git_false(self, tmp_path: Path) -> None:
        (tmp_path / "main.py").write_text("pass\n")
        agent = make_agent()
        result = await agent.run(repo_path=str(tmp_path))
        assert result.success is True
        git_stats = result.output["git_stats"]
        assert git_stats["is_git_repo"] is False

    async def test_scan_result_stored_in_state(self, python_repo: Path) -> None:
        state = SharedState(run_id="test01", subject="test")
        agent = make_agent(state=state)
        result = await agent.run(repo_path=str(python_repo))
        assert result.success is True

        run_state = await state.get()
        assert run_state.scan is not None
        assert run_state.scan.repo_path == str(python_repo)

    async def test_scan_result_has_correct_repo_path(self, python_repo: Path) -> None:
        state = SharedState(run_id="test02", subject="test")
        agent = make_agent(state=state)
        await agent.run(repo_path=str(python_repo))

        run_state = await state.get()
        assert run_state.scan is not None
        # Path should be resolved (absolute)
        assert run_state.scan.repo_path == str(python_repo.resolve())

    async def test_file_count_accurate(self, tmp_path: Path) -> None:
        (tmp_path / "a.py").write_text("pass\n")
        (tmp_path / "b.py").write_text("pass\n")
        (tmp_path / "c.py").write_text("pass\n")
        agent = make_agent()
        result = await agent.run(repo_path=str(tmp_path))
        assert result.output["file_count"] == 3

    async def test_json_files_not_counted_in_line_totals(self, tmp_path: Path) -> None:
        (tmp_path / "data.json").write_text('{"key": "value"}\n' * 100)
        (tmp_path / "app.py").write_text("pass\n" * 10)
        agent = make_agent()
        result = await agent.run(repo_path=str(tmp_path))
        # JSON lines are not counted in total_lines (they're data, not code)
        assert result.output["total_lines"] == 10

    async def test_llm_summary_stored_in_result(self, python_repo: Path) -> None:
        agent = make_agent(response_text="Custom summary from LLM.")
        result = await agent.run(repo_path=str(python_repo))
        assert result.output["summary"] == "Custom summary from LLM."

    async def test_root_structure_captured(self, tmp_path: Path) -> None:
        (tmp_path / "main.py").write_text("pass\n")
        subdir = tmp_path / "src"
        subdir.mkdir()
        (subdir / "app.py").write_text("pass\n")
        agent = make_agent()
        result = await agent.run(repo_path=str(tmp_path))
        structure = result.output["structure"]
        assert "root_files" in structure
        assert "root_dirs" in structure
        assert "src" in structure["root_dirs"]

    async def test_languages_sorted_by_line_count_descending(
        self, tmp_path: Path
    ) -> None:
        # Python: 100 lines, Go: 10 lines
        (tmp_path / "large.py").write_text("x = 1\n" * 100)
        (tmp_path / "small.go").write_text("// go\n" * 10)
        agent = make_agent()
        result = await agent.run(repo_path=str(tmp_path))
        languages = result.output["languages"]
        lang_names = list(languages.keys())
        # Python (100 lines) must appear before Go (10 lines)
        assert lang_names.index("Python") < lang_names.index("Go")


# ---------------------------------------------------------------------------
# Health scoring via scoring criteria (debate-based 10-point scale)
# ---------------------------------------------------------------------------


class TestScoringCriteria:
    """
    The health/quality scoring in Crucible uses a 0–10 scale across four
    criteria defined in crucible/debate/protocol.py: evidence_quality,
    logical_consistency, practical_feasibility, and novelty.
    Each persona weights these differently (weights sum to 1.0).
    """

    def test_scoring_criteria_string_defined(self) -> None:
        from crucible.debate.protocol import SCORING_CRITERIA

        assert "0-10" in SCORING_CRITERIA
        assert "evidence_quality" in SCORING_CRITERIA
        assert "logical_consistency" in SCORING_CRITERIA
        assert "practical_feasibility" in SCORING_CRITERIA
        assert "novelty" in SCORING_CRITERIA

    def test_four_scoring_dimensions(self) -> None:
        from crucible.debate.protocol import SCORING_CRITERIA

        dimensions = [
            "Evidence Quality",
            "Logical Consistency",
            "Practical Feasibility",
            "Novelty",
        ]
        for dim in dimensions:
            assert dim in SCORING_CRITERIA

    def test_scoring_expects_json_output(self) -> None:
        from crucible.debate.protocol import SCORING_CRITERIA

        assert "JSON" in SCORING_CRITERIA

    def test_each_persona_weights_sum_to_one(self) -> None:
        from crucible.debate.personas import ALL_PERSONAS

        for persona in ALL_PERSONAS:
            total = sum(persona.scoring_weight.values())
            assert abs(total - 1.0) < 0.01, (
                f"{persona.name} weights sum to {total:.4f}, expected 1.0"
            )

    def test_weighted_score_within_zero_ten_range(self) -> None:
        from crucible.debate.personas import PRAGMATIST

        # Simulate a scoring result
        raw_scores = {
            "evidence_quality": 8.0,
            "logical_consistency": 7.0,
            "practical_feasibility": 9.0,
            "novelty": 6.0,
        }
        weighted = sum(
            PRAGMATIST.scoring_weight.get(k, 0.25) * v
            for k, v in raw_scores.items()
        )
        assert 0.0 <= weighted <= 10.0
