"""Tests for template versioning and community submissions."""

from __future__ import annotations

import shutil
import textwrap
from pathlib import Path

import pytest

from crucible.templates.versioning import (
    TemplateVersion,
    VersionedTemplate,
    is_compatible,
    version_from_string,
)
from crucible.templates.community import (
    CommunityRegistry,
    TemplateSubmission,
    ValidationError,
    validate_submission,
    install_template,
    list_community_templates,
    _INSTALLED_DIR,
)
from crucible.templates import registry


# ---------------------------------------------------------------------------
# TemplateVersion parsing
# ---------------------------------------------------------------------------

class TestVersionParsing:
    def test_parses_valid_version(self) -> None:
        v = version_from_string("1.2.3")
        assert v == TemplateVersion(1, 2, 3)

    def test_parses_zeros(self) -> None:
        v = version_from_string("0.0.0")
        assert v == TemplateVersion(0, 0, 0)

    def test_parses_large_numbers(self) -> None:
        v = version_from_string("100.200.300")
        assert v == TemplateVersion(100, 200, 300)

    def test_strips_whitespace(self) -> None:
        v = version_from_string("  2.0.1  ")
        assert v == TemplateVersion(2, 0, 1)

    def test_invalid_too_few_parts(self) -> None:
        with pytest.raises(ValueError, match="major.minor.patch"):
            version_from_string("1.2")

    def test_invalid_too_many_parts(self) -> None:
        with pytest.raises(ValueError, match="major.minor.patch"):
            version_from_string("1.2.3.4")

    def test_invalid_non_integer(self) -> None:
        with pytest.raises(ValueError, match="integers"):
            version_from_string("1.x.3")

    def test_invalid_negative(self) -> None:
        with pytest.raises(ValueError, match="non-negative"):
            version_from_string("1.-1.0")

    def test_str_roundtrip(self) -> None:
        assert str(version_from_string("3.14.159")) == "3.14.159"


# ---------------------------------------------------------------------------
# TemplateVersion comparison
# ---------------------------------------------------------------------------

class TestVersionComparison:
    def test_equal_versions(self) -> None:
        assert version_from_string("1.0.0") == version_from_string("1.0.0")

    def test_major_ordering(self) -> None:
        assert version_from_string("2.0.0") > version_from_string("1.9.9")

    def test_minor_ordering(self) -> None:
        assert version_from_string("1.2.0") > version_from_string("1.1.9")

    def test_patch_ordering(self) -> None:
        assert version_from_string("1.0.2") > version_from_string("1.0.1")

    def test_less_than(self) -> None:
        assert version_from_string("0.9.0") < version_from_string("1.0.0")

    def test_dataclass_order(self) -> None:
        versions = [
            version_from_string("2.0.0"),
            version_from_string("1.0.0"),
            version_from_string("1.1.0"),
        ]
        assert sorted(versions) == [
            version_from_string("1.0.0"),
            version_from_string("1.1.0"),
            version_from_string("2.0.0"),
        ]


# ---------------------------------------------------------------------------
# is_compatible
# ---------------------------------------------------------------------------

class TestIsCompatible:
    def test_exact_match_is_compatible(self) -> None:
        req = version_from_string("1.2.3")
        avail = version_from_string("1.2.3")
        assert is_compatible(req, avail)

    def test_higher_minor_is_compatible(self) -> None:
        req = version_from_string("1.2.0")
        avail = version_from_string("1.3.0")
        assert is_compatible(req, avail)

    def test_higher_patch_same_minor_is_compatible(self) -> None:
        req = version_from_string("1.2.3")
        avail = version_from_string("1.2.5")
        assert is_compatible(req, avail)

    def test_lower_patch_is_not_compatible(self) -> None:
        req = version_from_string("1.2.5")
        avail = version_from_string("1.2.3")
        assert not is_compatible(req, avail)

    def test_lower_minor_is_not_compatible(self) -> None:
        req = version_from_string("1.3.0")
        avail = version_from_string("1.2.9")
        assert not is_compatible(req, avail)

    def test_different_major_is_not_compatible(self) -> None:
        req = version_from_string("1.0.0")
        avail = version_from_string("2.0.0")
        assert not is_compatible(req, avail)

    def test_older_major_is_not_compatible(self) -> None:
        req = version_from_string("2.0.0")
        avail = version_from_string("1.9.9")
        assert not is_compatible(req, avail)

    def test_zero_major_versions(self) -> None:
        req = version_from_string("0.1.0")
        avail = version_from_string("0.1.5")
        assert is_compatible(req, avail)


# ---------------------------------------------------------------------------
# VersionedTemplate
# ---------------------------------------------------------------------------

class TestVersionedTemplate:
    def test_version_property(self) -> None:
        tmpl = registry.get_template("seo_article")
        vt = VersionedTemplate(template=tmpl, author="Test Author")
        assert vt.version == version_from_string("1.0.0")

    def test_add_changelog_entry(self) -> None:
        tmpl = registry.get_template("market_research")
        vt = VersionedTemplate(template=tmpl)
        vt.add_changelog_entry("1.0.0", "Initial release")
        vt.add_changelog_entry("1.1.0", "Added competitor scanner improvements")
        assert vt.latest_changes() == "Added competitor scanner improvements"
        assert len(vt.changelog) == 2

    def test_latest_changes_empty(self) -> None:
        tmpl = registry.get_template("seo_article")
        vt = VersionedTemplate(template=tmpl)
        assert vt.latest_changes() is None

    def test_defaults(self) -> None:
        tmpl = registry.get_template("newsletter")
        vt = VersionedTemplate(template=tmpl)
        assert vt.author == ""
        assert vt.license == "MIT"
        assert vt.changelog == []


# ---------------------------------------------------------------------------
# Built-in template version metadata
# ---------------------------------------------------------------------------

class TestBuiltInTemplateVersionMetadata:
    def test_all_templates_have_version(self) -> None:
        templates = registry.list_templates()
        for t in templates:
            v = version_from_string(t.version)
            assert v.major >= 1 or v.minor >= 0, (
                f"Template '{t.name}' version '{t.version}' looks invalid"
            )

    def test_seo_article_version(self) -> None:
        tmpl = registry.get_template("seo_article")
        assert tmpl.version == "1.0.0"

    def test_template_has_license_field(self) -> None:
        tmpl = registry.get_template("web_app")
        assert isinstance(tmpl.license, str)

    def test_template_has_author_field(self) -> None:
        tmpl = registry.get_template("market_research")
        assert isinstance(tmpl.author, str)


# ---------------------------------------------------------------------------
# validate_submission
# ---------------------------------------------------------------------------

class TestValidateSubmission:
    def test_example_submission_passes(self) -> None:
        example = (
            Path(__file__).parent.parent
            / "crucible/templates/community_templates/example_submission"
        )
        submission = validate_submission(example)
        assert submission.name == "oss_health_audit"
        assert submission.author != ""
        assert submission.description != ""

    def test_missing_path_raises(self) -> None:
        with pytest.raises(ValidationError, match="does not exist"):
            validate_submission("/tmp/nonexistent_crucible_template_xyz")

    def test_missing_submission_attr_raises(self, tmp_path: Path) -> None:
        module_file = tmp_path / "bad_template.py"
        module_file.write_text(textwrap.dedent("""
            from crucible.templates.base import AgentSpec, Template, template
            from crucible.core.agent import AgentConfig

            TEMPLATE = template(Template(
                name="bad_t",
                description="A test template with enough description here.",
                category="Test",
                agents=[
                    AgentSpec(name="A1", role="r1", instructions="i1" * 30),
                    AgentSpec(name="A2", role="r2", instructions="i2" * 30),
                ],
                debate_topics=["topic"],
                expected_outputs=["output"],
            ))
        """))
        with pytest.raises(ValidationError, match="SUBMISSION"):
            validate_submission(module_file)

    def test_missing_template_attr_raises(self, tmp_path: Path) -> None:
        module_file = tmp_path / "no_template.py"
        module_file.write_text(textwrap.dedent("""
            from crucible.templates.community import TemplateSubmission
            SUBMISSION = TemplateSubmission(
                name="no_tmpl",
                author="Author",
                description="desc",
                version="1.0.0",
                license="MIT",
            )
        """))
        with pytest.raises(ValidationError, match="TEMPLATE"):
            validate_submission(module_file)

    def test_too_few_agents_raises(self, tmp_path: Path) -> None:
        module_file = tmp_path / "one_agent.py"
        module_file.write_text(textwrap.dedent("""
            from crucible.templates.base import AgentSpec, Template, template
            from crucible.templates.community import TemplateSubmission
            from crucible.core.agent import AgentConfig

            SUBMISSION = TemplateSubmission(
                name="one_agent_t",
                author="Author",
                description="A template with only one agent.",
                version="1.0.0",
                license="MIT",
            )
            TEMPLATE = template(Template(
                name="one_agent_t",
                description="One agent template.",
                category="Test",
                agents=[
                    AgentSpec(name="Only", role="role", instructions="instructions here"),
                ],
                debate_topics=["topic"],
                expected_outputs=["output"],
            ))
        """))
        with pytest.raises(ValidationError, match="at least 2 agents"):
            validate_submission(module_file)

    def test_missing_debate_topics_raises(self, tmp_path: Path) -> None:
        module_file = tmp_path / "no_debate.py"
        module_file.write_text(textwrap.dedent("""
            from crucible.templates.base import AgentSpec, Template, template
            from crucible.templates.community import TemplateSubmission
            from crucible.core.agent import AgentConfig

            SUBMISSION = TemplateSubmission(
                name="no_debate_t",
                author="Author",
                description="Template with no debate topics.",
                version="1.0.0",
                license="MIT",
            )
            TEMPLATE = template(Template(
                name="no_debate_t",
                description="No debate template.",
                category="Test",
                agents=[
                    AgentSpec(name="A1", role="r", instructions="instructions go here" * 3),
                    AgentSpec(name="A2", role="r", instructions="instructions go here" * 3),
                ],
                debate_topics=[],
                expected_outputs=["output"],
            ))
        """))
        with pytest.raises(ValidationError, match="debate topic"):
            validate_submission(module_file)

    def test_missing_expected_outputs_raises(self, tmp_path: Path) -> None:
        module_file = tmp_path / "no_outputs.py"
        module_file.write_text(textwrap.dedent("""
            from crucible.templates.base import AgentSpec, Template, template
            from crucible.templates.community import TemplateSubmission
            from crucible.core.agent import AgentConfig

            SUBMISSION = TemplateSubmission(
                name="no_outputs_t",
                author="Author",
                description="Template with no expected outputs.",
                version="1.0.0",
                license="MIT",
            )
            TEMPLATE = template(Template(
                name="no_outputs_t",
                description="No outputs template.",
                category="Test",
                agents=[
                    AgentSpec(name="A1", role="r", instructions="instructions go here" * 3),
                    AgentSpec(name="A2", role="r", instructions="instructions go here" * 3),
                ],
                debate_topics=["topic"],
                expected_outputs=[],
            ))
        """))
        with pytest.raises(ValidationError, match="expected output"):
            validate_submission(module_file)

    def test_empty_author_raises(self, tmp_path: Path) -> None:
        module_file = tmp_path / "no_author.py"
        module_file.write_text(textwrap.dedent("""
            from crucible.templates.base import AgentSpec, Template, template
            from crucible.templates.community import TemplateSubmission
            from crucible.core.agent import AgentConfig

            SUBMISSION = TemplateSubmission(
                name="no_author_t",
                author="",
                description="Has no author.",
                version="1.0.0",
                license="MIT",
            )
            TEMPLATE = template(Template(
                name="no_author_t",
                description="No author template.",
                category="Test",
                agents=[
                    AgentSpec(name="A1", role="r", instructions="instructions go here" * 3),
                    AgentSpec(name="A2", role="r", instructions="instructions go here" * 3),
                ],
                debate_topics=["topic"],
                expected_outputs=["output"],
            ))
        """))
        with pytest.raises(ValidationError, match="author"):
            validate_submission(module_file)


# ---------------------------------------------------------------------------
# install_template and list_community_templates
# ---------------------------------------------------------------------------

class TestCommunityInstallation:
    """Tests that install into a temp directory so as not to pollute the real installed dir."""

    def _make_valid_module(self, tmp_path: Path, name: str = "test_community_tmpl") -> Path:
        module_dir = tmp_path / name
        module_dir.mkdir()
        (module_dir / "__init__.py").write_text(textwrap.dedent(f"""
            from crucible.templates.base import AgentSpec, Template, template
            from crucible.templates.community import TemplateSubmission
            from crucible.core.agent import AgentConfig

            SUBMISSION = TemplateSubmission(
                name="{name}",
                author="Test Author <test@example.com>",
                description="A valid community template for testing.",
                version="1.0.0",
                license="MIT",
                tags=["test"],
            )
            TEMPLATE = template(Template(
                name="{name}",
                description="A valid community template for testing.",
                category="Test",
                agents=[
                    AgentSpec(
                        name="Agent One",
                        role="Primary specialist",
                        instructions="You are a specialist. Analyze the topic thoroughly and produce detailed findings.",
                    ),
                    AgentSpec(
                        name="Agent Two",
                        role="Secondary specialist",
                        instructions="You are a secondary specialist. Review findings and provide recommendations.",
                    ),
                ],
                debate_topics=["Which approach is best?", "Option A", "Option B"],
                expected_outputs=["Analysis report", "Recommendations"],
            ))
        """))
        return module_dir

    def test_install_valid_template(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        install_dir = tmp_path / "installed"
        monkeypatch.setattr(
            "crucible.templates.community._INSTALLED_DIR", install_dir
        )
        src = self._make_valid_module(tmp_path)
        name = install_template(src)
        assert name == "test_community_tmpl"
        assert (install_dir / src.name).exists()

    def test_install_invalid_template_raises(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        install_dir = tmp_path / "installed"
        monkeypatch.setattr(
            "crucible.templates.community._INSTALLED_DIR", install_dir
        )
        bad = tmp_path / "bad"
        bad.mkdir()
        (bad / "__init__.py").write_text("# empty module")
        with pytest.raises(ValidationError):
            install_template(bad)

    def test_install_duplicate_raises(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        install_dir = tmp_path / "installed"
        monkeypatch.setattr(
            "crucible.templates.community._INSTALLED_DIR", install_dir
        )
        src = self._make_valid_module(tmp_path)
        install_template(src)
        with pytest.raises(FileExistsError):
            install_template(src)

    def test_list_community_templates_empty(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        install_dir = tmp_path / "installed_empty"
        monkeypatch.setattr(
            "crucible.templates.community._INSTALLED_DIR", install_dir
        )
        result = list_community_templates()
        assert result == []

    def test_list_community_templates_after_install(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        install_dir = tmp_path / "installed2"
        monkeypatch.setattr(
            "crucible.templates.community._INSTALLED_DIR", install_dir
        )
        src = self._make_valid_module(tmp_path, name="list_test_tmpl")
        install_template(src)
        entries = list_community_templates()
        assert len(entries) == 1
        assert entries[0]["name"] == "list_test_tmpl"
        assert entries[0]["author"] == "Test Author <test@example.com>"
        assert entries[0]["version"] == "1.0.0"
        assert entries[0]["license"] == "MIT"


# ---------------------------------------------------------------------------
# CommunityRegistry
# ---------------------------------------------------------------------------

class TestCommunityRegistry:
    def test_list_returns_empty_for_nonexistent_dir(self, tmp_path: Path) -> None:
        reg = CommunityRegistry(community_dir=tmp_path / "nonexistent")
        assert reg.list() == []

    def test_get_raises_for_unknown_template(self, tmp_path: Path) -> None:
        reg = CommunityRegistry(community_dir=tmp_path / "empty_dir")
        with pytest.raises(KeyError, match="not found"):
            reg.get("totally_unknown_zzz")
