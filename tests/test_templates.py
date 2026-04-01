"""Tests for the Agent Template Marketplace."""

from __future__ import annotations

import pytest
from crucible.templates import registry, Template, AgentSpec, TemplateSession
from crucible.templates.base import _REGISTRY
from crucible.core.agent import AgentConfig


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_all_templates() -> list[Template]:
    """Force-load all templates and return the full list."""
    return registry.list_templates()


# ---------------------------------------------------------------------------
# Registry discovery
# ---------------------------------------------------------------------------

class TestRegistryDiscovery:
    def test_registry_discovers_templates(self) -> None:
        templates = get_all_templates()
        assert len(templates) >= 50, (
            f"Expected at least 50 templates, found {len(templates)}"
        )

    def test_list_templates_sorted(self) -> None:
        templates = get_all_templates()
        categories = [t.category for t in templates]
        names_per_cat: dict[str, list[str]] = {}
        for t in templates:
            names_per_cat.setdefault(t.category, []).append(t.name)
        # Verify sorted by category then name within each category
        for cat, names in names_per_cat.items():
            assert names == sorted(names), (
                f"Templates in category '{cat}' are not sorted by name"
            )

    def test_list_categories_returns_dict(self) -> None:
        cats = registry.list_categories()
        assert isinstance(cats, dict)
        assert len(cats) >= 10, f"Expected at least 10 categories, found {len(cats)}"
        expected_categories = {
            "Content & Marketing",
            "Software Development",
            "Research & Analysis",
            "Business Operations",
            "Creative",
            "Education",
            "E-commerce",
            "Finance",
            "HR & Recruiting",
            "Sales",
        }
        actual = set(cats.keys())
        missing = expected_categories - actual
        assert not missing, f"Missing categories: {missing}"

    def test_get_template_by_name(self) -> None:
        tmpl = registry.get_template("seo_article")
        assert tmpl.name == "seo_article"
        assert tmpl.category == "Content & Marketing"

    def test_get_template_unknown_raises_key_error(self) -> None:
        with pytest.raises(KeyError, match="not found"):
            registry.get_template("nonexistent_template_xyz")

    def test_search_returns_results(self) -> None:
        results = registry.search("marketing")
        assert len(results) > 0
        for t in results:
            assert (
                "marketing" in t.name.lower()
                or "marketing" in t.description.lower()
                or any("marketing" in tag.lower() for tag in t.tags)
            )

    def test_search_case_insensitive(self) -> None:
        lower = registry.search("seo")
        upper = registry.search("SEO")
        assert set(t.name for t in lower) == set(t.name for t in upper)

    def test_search_no_results(self) -> None:
        results = registry.search("zzz_nonexistent_zzz")
        assert results == []

    def test_deploy_template_returns_session(self) -> None:
        session = registry.deploy_template("newsletter")
        assert isinstance(session, TemplateSession)
        assert session.template.name == "newsletter"


# ---------------------------------------------------------------------------
# Template data integrity
# ---------------------------------------------------------------------------

class TestTemplateDataIntegrity:
    @pytest.mark.parametrize("template", get_all_templates())
    def test_required_fields_present(self, template: Template) -> None:
        assert template.name, f"Template missing name: {template}"
        assert template.description, f"Template '{template.name}' missing description"
        assert template.category, f"Template '{template.name}' missing category"
        assert template.agents, f"Template '{template.name}' has no agents"
        assert template.expected_outputs, (
            f"Template '{template.name}' has no expected_outputs"
        )

    @pytest.mark.parametrize("template", get_all_templates())
    def test_agent_specs_valid(self, template: Template) -> None:
        for agent in template.agents:
            assert isinstance(agent, AgentSpec), (
                f"Template '{template.name}' agent is not AgentSpec: {agent}"
            )
            assert agent.name, f"Template '{template.name}' has agent with no name"
            assert agent.role, f"Template '{template.name}' agent '{agent.name}' has no role"
            assert agent.instructions, (
                f"Template '{template.name}' agent '{agent.name}' has no instructions"
            )
            assert isinstance(agent.config, AgentConfig), (
                f"Template '{template.name}' agent '{agent.name}' config is not AgentConfig"
            )

    @pytest.mark.parametrize("template", get_all_templates())
    def test_minimum_agents(self, template: Template) -> None:
        assert len(template.agents) >= 2, (
            f"Template '{template.name}' has fewer than 2 agents: {len(template.agents)}"
        )

    @pytest.mark.parametrize("template", get_all_templates())
    def test_minimum_expected_outputs(self, template: Template) -> None:
        assert len(template.expected_outputs) >= 3, (
            f"Template '{template.name}' has fewer than 3 expected outputs"
        )

    @pytest.mark.parametrize("template", get_all_templates())
    def test_description_is_substantive(self, template: Template) -> None:
        assert len(template.description) >= 30, (
            f"Template '{template.name}' description is too short: '{template.description}'"
        )

    @pytest.mark.parametrize("template", get_all_templates())
    def test_agent_instructions_substantive(self, template: Template) -> None:
        for agent in template.agents:
            assert len(agent.instructions) >= 50, (
                f"Template '{template.name}' agent '{agent.name}' instructions too short"
            )

    @pytest.mark.parametrize("template", get_all_templates())
    def test_agent_names_unique_within_template(self, template: Template) -> None:
        names = [a.name for a in template.agents]
        assert len(names) == len(set(names)), (
            f"Template '{template.name}' has duplicate agent names: {names}"
        )

    @pytest.mark.parametrize("template", get_all_templates())
    def test_version_format(self, template: Template) -> None:
        parts = template.version.split(".")
        assert len(parts) >= 2, (
            f"Template '{template.name}' version '{template.version}' is not semver-like"
        )

    @pytest.mark.parametrize("template", get_all_templates())
    def test_tags_is_list(self, template: Template) -> None:
        assert isinstance(template.tags, list), (
            f"Template '{template.name}' tags is not a list"
        )


# ---------------------------------------------------------------------------
# Category coverage
# ---------------------------------------------------------------------------

class TestCategoryCoverage:
    REQUIRED_TEMPLATES = [
        "seo_article",
        "social_media_campaign",
        "newsletter",
        "web_app",
        "mobile_app",
        "api_service",
        "chrome_extension",
        "market_research",
        "codebase_audit",
        "academic_paper",
        "startup_pitch",
        "product_spec",
        "legal_review",
        "video_script",
        "course_creator",
        "game_design",
        "lesson_plan",
        "tutoring_session",
        "exam_prep",
        "curriculum_design",
        "research_paper_review",
        "product_listing_optimizer",
        "competitor_pricing",
        "customer_review_analysis",
        "inventory_forecaster",
        "wellness_plan",
        "patient_intake_summarizer",
        "symptom_checker_research",
        "property_analysis",
        "market_comparison",
        "listing_generator",
        "financial_model",
        "investment_thesis",
        "budget_planner",
        "tax_prep_organizer",
        "job_description_writer",
        "resume_screener",
        "interview_prep",
        "onboarding_plan",
        "incident_postmortem",
        "capacity_planning",
        "migration_planner",
        "monitoring_setup",
        "dataset_explorer",
        "ml_pipeline",
        "ab_test_analyzer",
        "dashboard_builder",
        "patent_analysis",
        "compliance_audit",
        "terms_of_service_generator",
        "gdpr_assessment",
        "cold_outreach_sequence",
        "deal_qualification",
        "proposal_generator",
        "win_loss_analysis",
        "churn_predictor",
        "qbr_prep",
        "feature_request_aggregator",
        "onboarding_playbook",
        "weekly_planner",
        "meeting_prep",
        "goal_tracker",
        "habit_builder",
        "investigative_research",
        "fact_checker",
        "story_pitch",
    ]

    def test_all_required_templates_exist(self) -> None:
        templates = get_all_templates()
        names = {t.name for t in templates}
        missing = [n for n in self.REQUIRED_TEMPLATES if n not in names]
        assert not missing, f"Missing required templates: {missing}"

    def test_template_names_are_snake_case(self) -> None:
        templates = get_all_templates()
        for t in templates:
            assert t.name == t.name.lower(), (
                f"Template name '{t.name}' is not lowercase"
            )
            assert " " not in t.name, (
                f"Template name '{t.name}' contains spaces (use underscores)"
            )


# ---------------------------------------------------------------------------
# TemplateSession plan (no network required)
# ---------------------------------------------------------------------------

class TestTemplateSessionPlan:
    def test_plan_returns_dict(self) -> None:
        session = registry.deploy_template("seo_article")
        plan = session.plan()
        assert isinstance(plan, dict)

    def test_plan_has_required_keys(self) -> None:
        session = registry.deploy_template("seo_article")
        plan = session.plan()
        assert "template" in plan
        assert "category" in plan
        assert "agents" in plan
        assert "expected_outputs" in plan
        assert "debate_topics" in plan

    def test_plan_agents_list(self) -> None:
        session = registry.deploy_template("web_app")
        plan = session.plan()
        for agent in plan["agents"]:
            assert "name" in agent
            assert "role" in agent

    def test_session_stores_template(self) -> None:
        session = registry.deploy_template("game_design")
        assert session.template.name == "game_design"
        assert session.template.category == "Creative"


# ---------------------------------------------------------------------------
# Specific template content tests
# ---------------------------------------------------------------------------

class TestSpecificTemplates:
    def test_seo_article_has_five_agents(self) -> None:
        tmpl = registry.get_template("seo_article")
        assert len(tmpl.agents) == 5

    def test_web_app_has_debate_topics(self) -> None:
        tmpl = registry.get_template("web_app")
        assert len(tmpl.debate_topics) >= 2

    def test_legal_review_category(self) -> None:
        tmpl = registry.get_template("legal_review")
        assert tmpl.category == "Business Operations"

    def test_codebase_audit_category(self) -> None:
        tmpl = registry.get_template("codebase_audit")
        assert tmpl.category == "Research & Analysis"

    def test_gdpr_assessment_tags_include_privacy(self) -> None:
        tmpl = registry.get_template("gdpr_assessment")
        assert any("privacy" in tag.lower() or "gdpr" in tag.lower() for tag in tmpl.tags)

    def test_ml_pipeline_agents_include_mlops(self) -> None:
        tmpl = registry.get_template("ml_pipeline")
        agent_names = [a.name.lower() for a in tmpl.agents]
        assert any("mlops" in name or "deploy" in name or "ops" in name for name in agent_names)

    def test_startup_pitch_expected_outputs_include_deck(self) -> None:
        tmpl = registry.get_template("startup_pitch")
        outputs_text = " ".join(tmpl.expected_outputs).lower()
        assert "pitch" in outputs_text or "deck" in outputs_text

    def test_wellness_plan_not_medical_advice(self) -> None:
        """Wellness templates should include disclaimers in instructions."""
        tmpl = registry.get_template("wellness_plan")
        all_instructions = " ".join(a.instructions for a in tmpl.agents)
        assert any(
            phrase in all_instructions.lower()
            for phrase in ["not medical advice", "consult", "physician", "healthcare"]
        )

    def test_symptom_checker_has_emergency_flag(self) -> None:
        tmpl = registry.get_template("symptom_checker_research")
        all_instructions = " ".join(a.instructions for a in tmpl.agents)
        assert "red flag" in all_instructions.lower() or "emergency" in all_instructions.lower()
