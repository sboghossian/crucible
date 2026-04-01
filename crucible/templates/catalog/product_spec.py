"""Product specification and PRD team — Business Operations."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="product_spec",
    description="Produces a complete PRD with user stories, acceptance criteria, and scope debate from a product idea.",
    category="Business Operations",
    tags=["product", "prd", "user stories", "requirements", "product management"],
    agents=[
        AgentSpec(
            name="User Researcher",
            role="User needs and behavioral insight specialist",
            instructions=(
                "You are a user researcher. For the given product concept, produce: "
                "3 user personas with goals, behaviors, and pain points, "
                "user interview questions (15 questions to validate the concept), "
                "Jobs-to-be-Done statements for each persona, "
                "assumptions log (what we believe is true but haven't validated), "
                "success metrics from the user perspective (how will users know this works?), "
                "and edge case users we should design for (power users, accessibility needs, non-English speakers)."
            ),
            config=AgentConfig(max_tokens=3500),
        ),
        AgentSpec(
            name="Product Manager",
            role="PRD author and feature scope specialist",
            instructions=(
                "You are a senior product manager. Write a complete PRD: "
                "problem statement and opportunity (why build this?), "
                "goals and success metrics (OKR-format), "
                "scope table (in scope / out of scope / future consideration), "
                "feature breakdown with priority (Must Have / Should Have / Could Have / Won't Have), "
                "dependency map (what does this depend on? what depends on this?), "
                "rollout strategy (phased, feature flags, regional), "
                "and open questions requiring resolution before development starts."
            ),
            config=AgentConfig(max_tokens=4000),
        ),
        AgentSpec(
            name="Technical Writer",
            role="User stories and acceptance criteria specialist",
            instructions=(
                "You are a technical writer specializing in agile requirements. Write: "
                "user stories in 'As a [persona], I want [goal] so that [reason]' format for all features, "
                "acceptance criteria in Given/When/Then format for each story, "
                "edge case scenarios for the 5 most critical stories, "
                "error states and empty states for each major flow, "
                "and a story map organized by user journey phase."
            ),
            config=AgentConfig(max_tokens=4000),
        ),
        AgentSpec(
            name="Scope Reviewer",
            role="Scope challenge and MVP definition specialist",
            instructions=(
                "You are a product scope reviewer whose job is to cut scope ruthlessly. Evaluate: "
                "is each feature truly necessary for the core value proposition?, "
                "what is the absolute minimum viable product (MVP) that validates the key assumption?, "
                "which features add complexity without proportional value?, "
                "estimated development effort for each feature (S/M/L/XL t-shirt sizing), "
                "and a launch sequence recommendation: what ships in v1, v1.1, and v2?"
            ),
            config=AgentConfig(max_tokens=3000),
        ),
    ],
    debate_topics=[
        "What is the right scope for the MVP to maximize learning with minimal build?",
        "Narrow MVP: single persona, single flow, prove the core value hypothesis",
        "Broad MVP: full feature set for one segment to enable real usage patterns",
        "Concierge MVP: manual service delivery to validate before building",
        "Wizard-of-Oz MVP: fake the backend, validate front-end assumptions first",
    ],
    expected_outputs=[
        "Complete PRD document",
        "3 user personas with Jobs-to-be-Done",
        "Prioritized feature list (MoSCoW)",
        "User stories with acceptance criteria (Given/When/Then)",
        "Story map organized by journey phase",
        "MVP definition and v1/v2 launch sequence",
        "T-shirt size effort estimates",
        "Open questions log",
    ],
))
