"""Curriculum design team — Education."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="curriculum_design",
    description="Designs a complete educational curriculum for a program, track, or school subject with scope, sequence, and materials.",
    category="Education",
    tags=["curriculum", "program design", "scope and sequence", "educational program", "bootcamp"],
    agents=[
        AgentSpec(
            name="Needs Analyst",
            role="Learner needs and program context specialist",
            instructions=(
                "You are an educational needs analyst. Produce: "
                "target learner profile (current competencies, goals, constraints, context), "
                "program goals and graduate profile (what should learners be able to do on day 1 after completion?), "
                "stakeholder analysis (learners, instructors, employers, institutions), "
                "constraints inventory (time, budget, technology, instructor expertise), "
                "benchmark analysis (what are leading programs doing?), "
                "and learning outcomes framework (tied to industry standards or employer needs)."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Scope and Sequence Designer",
            role="Curriculum architecture and sequencing specialist",
            instructions=(
                "You are a curriculum architect. Design: "
                "full scope of content (all topics, grouped into units/modules), "
                "learning sequence with rationale (backward design from outcomes), "
                "horizontal alignment (connections across topics within a timeframe), "
                "vertical alignment (progression across levels), "
                "pacing guide (weeks per unit, hours per week), "
                "and a curriculum map (visual grid: units vs. outcomes vs. assessment)."
            ),
            config=AgentConfig(max_tokens=4000),
        ),
        AgentSpec(
            name="Materials Developer",
            role="Instructional materials and resource curation specialist",
            instructions=(
                "You are a materials development specialist. For 3 sample units, produce: "
                "unit overview (objectives, essential questions, key vocabulary), "
                "recommended readings and resources (textbooks, articles, videos, tools), "
                "lesson plan templates, "
                "student-facing materials (handouts, worksheets, project briefs), "
                "and instructor guides (facilitation notes, common student struggles, answers)."
            ),
            config=AgentConfig(max_tokens=4000),
        ),
        AgentSpec(
            name="Assessment Framework Designer",
            role="Program-level assessment and credentialing specialist",
            instructions=(
                "You are an assessment and credentialing specialist. Design: "
                "assessment strategy for the full program (formative, summative, capstone), "
                "competency-based progression criteria (when can students advance?), "
                "final capstone or portfolio requirements, "
                "grading philosophy (mastery-based vs. traditional), "
                "program-level data collection for continuous improvement, "
                "and a credential or certificate framework (badges, certificates, transcripts)."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
    ],
    debate_topics=[
        "What curriculum design model best serves this program's goals?",
        "Backward design (start from outcomes, design learning to achieve them)",
        "Competency-based (advance on mastery, not time), "
        "Project-based (authentic projects drive all content acquisition)",
        "Spiral curriculum (revisit concepts at increasing depth across levels)",
    ],
    expected_outputs=[
        "Program goals and graduate competency profile",
        "Full scope of content (all topics and units)",
        "Scope and sequence with pacing guide",
        "Curriculum map (units × outcomes × assessment)",
        "3 sample unit overviews with materials",
        "Program-level assessment framework",
        "Credential and badge framework",
    ],
))
