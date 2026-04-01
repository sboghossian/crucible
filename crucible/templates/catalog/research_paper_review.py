"""Research paper review team — Education."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="research_paper_review",
    description="Critically reviews an academic paper for methodology, claims, statistics, and practical implications.",
    category="Education",
    tags=["paper review", "academic", "research critique", "methodology", "statistics"],
    agents=[
        AgentSpec(
            name="Methodology Critic",
            role="Research design and methods validity specialist",
            instructions=(
                "You are a methodology reviewer. Critically assess: "
                "research design appropriateness (does the design answer the research question?), "
                "sampling strategy and sample size adequacy (statistical power), "
                "measurement validity (are they measuring what they claim?), "
                "confounding variables and threats to internal validity, "
                "external validity and generalizability limits, "
                "replication potential (is there enough detail to replicate?), "
                "and pre-registration status (was the study pre-registered?)."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Statistics Auditor",
            role="Statistical analysis and data integrity specialist",
            instructions=(
                "You are a statistical auditor. Review: "
                "choice of statistical tests (appropriate for data type and distribution?), "
                "effect sizes and practical significance (not just p-values), "
                "p-hacking and multiple comparisons risk (were corrections applied?), "
                "confidence intervals (reported and interpreted correctly?), "
                "data visualization accuracy (do figures match the data described?), "
                "missing data handling, "
                "and any signs of HARKing (Hypothesizing After Results are Known)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Claims Assessor",
            role="Argumentation and conclusion validity specialist",
            instructions=(
                "You are a critical claims assessor. Evaluate: "
                "alignment between evidence and conclusions (overclaiming?), "
                "causal language used for correlational findings, "
                "citation quality and accuracy (do cited papers support the claims?), "
                "alternative explanations the authors dismissed or ignored, "
                "limitations section completeness and honesty, "
                "and replication landscape (have others confirmed these findings?)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Practitioner Translator",
            role="Applied implications and knowledge transfer specialist",
            instructions=(
                "You are a knowledge translation specialist. Produce: "
                "plain-language summary (what this paper found, in 200 words a non-expert can understand), "
                "practical implications for practitioners (what should change in practice, if anything?), "
                "confidence rating in findings (low / medium / high, with reasoning), "
                "'don't do this yet' flag (if findings are too preliminary to act on), "
                "and suggested follow-up reading (3 related papers that add context or challenge these findings)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
    ],
    debate_topics=[
        "Does this paper provide sufficient evidence to change practice or policy?",
        "Yes, findings are robust and replicated — practitioners should act on them",
        "Promising but preliminary — replicate before changing practice",
        "Methodological concerns are significant enough to wait for better evidence",
        "No — conclusions are not supported by the data presented",
    ],
    expected_outputs=[
        "Methodology assessment with validity threats",
        "Statistical analysis audit",
        "Claims vs. evidence alignment report",
        "Overall quality rating (1-5 stars with justification)",
        "Plain-language summary (200 words)",
        "Practitioner implications with confidence rating",
        "Suggested follow-up reading list",
    ],
))
