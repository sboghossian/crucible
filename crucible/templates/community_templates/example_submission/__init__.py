"""Open-source project health audit — Software Development.

Community example template demonstrating the submission format.
This template assembles a team to evaluate an open-source repository's
health: code quality, community engagement, documentation, and security posture.
"""

from crucible.templates.base import AgentSpec, Template, template
from crucible.templates.community import TemplateSubmission
from crucible.core.agent import AgentConfig

# ---------------------------------------------------------------------------
# Submission metadata (required for community templates)
# ---------------------------------------------------------------------------

SUBMISSION = TemplateSubmission(
    name="oss_health_audit",
    author="Crucible Team <crucible@example.com>",
    description=(
        "Evaluates an open-source project's health across code quality, "
        "documentation, community engagement, and security posture."
    ),
    version="1.0.0",
    license="MIT",
    tags=["open source", "audit", "code quality", "security", "documentation"],
    tested_with_crucible_version="1.0.0",
)

# ---------------------------------------------------------------------------
# Template definition
# ---------------------------------------------------------------------------

TEMPLATE = template(Template(
    name="oss_health_audit",
    description=(
        "Evaluates an open-source project's health across code quality, "
        "documentation, community engagement, and security posture."
    ),
    category="Software Development",
    tags=["open source", "audit", "code quality", "security", "documentation"],
    version="1.0.0",
    author="Crucible Team",
    license="MIT",
    agents=[
        AgentSpec(
            name="Code Quality Reviewer",
            role="Static analysis and code health specialist",
            instructions=(
                "You are a senior software engineer specializing in code quality. "
                "For the given open-source project, assess: "
                "code organization and architecture patterns, "
                "test coverage signals (presence of test directories, CI badges), "
                "dependency health (number of deps, last updated, known vulnerabilities), "
                "coding standards adherence (linting configs, formatting), "
                "technical debt indicators (TODO comments, deprecated APIs, dead code), "
                "and build/CI pipeline maturity. "
                "Score the project 1-10 on code health with specific evidence."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Documentation Analyst",
            role="Documentation quality and completeness evaluator",
            instructions=(
                "You are a technical writer and developer experience specialist. "
                "Evaluate the project's documentation: "
                "README quality (installation, quick start, API reference), "
                "presence of contributing guide (CONTRIBUTING.md), "
                "changelog or release notes (CHANGELOG.md), "
                "code of conduct, "
                "inline code documentation (docstrings, comments), "
                "examples and tutorials, "
                "and API documentation if applicable. "
                "Score documentation 1-10 and list the three biggest gaps."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
        AgentSpec(
            name="Community Health Analyst",
            role="Open source community engagement specialist",
            instructions=(
                "You are a community analyst specializing in open-source ecosystems. "
                "Assess the project community: "
                "contributor diversity (number of unique contributors, bus factor risk), "
                "issue response time signals, "
                "PR merge cadence, "
                "release frequency and versioning discipline (semver compliance), "
                "community governance (maintainers listed, decision-making process), "
                "and adoption signals (stars, forks, dependent projects). "
                "Flag any bus-factor or abandonment risks explicitly."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
        AgentSpec(
            name="Security Posture Reviewer",
            role="Open source security and supply chain risk assessor",
            instructions=(
                "You are a security engineer focused on open-source risk. "
                "Review: security policy presence (SECURITY.md), "
                "dependency pinning practices, "
                "secrets scanning configuration, "
                "signed releases or provenance attestation, "
                "known CVE history, "
                "supply chain risk (maintainer account security, publishing pipeline), "
                "and license compliance (license file, SPDX headers). "
                "Produce a risk tier (Low / Medium / High) with justification."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
        AgentSpec(
            name="Health Report Writer",
            role="Executive summary and recommendations synthesizer",
            instructions=(
                "You are a technical analyst writing for engineering leadership. "
                "Synthesize all specialist findings into: "
                "an overall health score (1-10) with component breakdown, "
                "a traffic-light summary (Green/Yellow/Red per dimension), "
                "top 3 strengths to celebrate, "
                "top 3 risks to address immediately, "
                "a prioritized improvement roadmap (Quick wins / 30-day / 90-day), "
                "and a 'should we adopt this?' recommendation with caveats. "
                "Format for a busy engineering director: bullet-heavy, no filler."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
    ],
    debate_topics=[
        "Is this project safe and mature enough for production adoption?",
        "Yes — production-ready with standard due diligence",
        "Yes, with mitigations — adopt but address the top risks first",
        "No — wait for the project to mature further",
        "Hard no — too many red flags, seek alternatives",
    ],
    expected_outputs=[
        "Overall health score (1-10) with component breakdown",
        "Code quality assessment with technical debt inventory",
        "Documentation gap analysis with prioritized fixes",
        "Community health report with bus-factor assessment",
        "Security posture review with risk tier",
        "Traffic-light summary (Green/Yellow/Red per dimension)",
        "Prioritized improvement roadmap",
        "'Should we adopt?' recommendation",
    ],
))
