"""Fact-checking team — Media & Journalism."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="fact_checker",
    description="Systematically fact-checks claims in a document, speech, or article with source verification and accuracy ratings.",
    category="Media & Journalism",
    tags=["fact checking", "journalism", "misinformation", "verification", "accuracy"],
    agents=[
        AgentSpec(
            name="Claim Extractor",
            role="Factual claim identification specialist",
            instructions=(
                "You are a fact-checking analyst. From the given content, extract: "
                "all verifiable factual claims (statistics, dates, names, events, quotes, attributions), "
                "opinion statements that should NOT be fact-checked (clearly labeled as such), "
                "implied claims (what is assumed to be true but not explicitly stated?), "
                "claims most likely to be inaccurate (statistical claims, old data cited as current, precise numbers), "
                "and a priority ranking (which claims, if false, would most damage credibility?)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Source Verifier",
            role="Primary source research and verification specialist",
            instructions=(
                "You are a fact-checking researcher. For each claim, define: "
                "authoritative primary sources to verify against (government data, peer-reviewed research, official records), "
                "how to trace a statistic to its original source (avoiding citation chains), "
                "source quality assessment criteria (recency, methodology, conflicts of interest), "
                "context needed to assess accuracy (is the claim misleading even if technically true?), "
                "and a verification checklist for quotes (did this person say this, in this context?)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Accuracy Rater",
            role="Truth rating and context specialist",
            instructions=(
                "You are a fact-checking editor. Rate each claim on a 5-point scale: "
                "True (accurate and in context), "
                "Mostly True (accurate but missing important context), "
                "Half True (partially accurate, but significant omissions), "
                "Mostly False (contains a grain of truth but primarily misleading), "
                "False (demonstrably inaccurate). "
                "For each rating: explain the evidence, explain the missing context, "
                "and provide the corrected or complete version of the claim."
            ),
            config=AgentConfig(max_tokens=3500),
        ),
        AgentSpec(
            name="Report Writer",
            role="Fact-check publication and editor briefing specialist",
            instructions=(
                "You are a fact-check report writer. Produce: "
                "executive summary of fact-check findings, "
                "full fact-check article with ratings, evidence, and corrections, "
                "editor briefing memo (what to require the author to fix before publication), "
                "legal risk assessment (any claims that could create defamation liability?), "
                "and a reader-facing correction notice template (if content is already published)."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
    ],
    debate_topics=[
        "At what accuracy threshold should a piece be published, retracted, or corrected?",
        "Zero tolerance: any false claim must be corrected before publication",
        "Material accuracy: minor errors acceptable if they don't change the essential truth",
        "Publish with correction: publish and immediately append correction with visible notice",
    ],
    expected_outputs=[
        "Prioritized list of verifiable claims",
        "Primary source verification strategy",
        "Accuracy rating for each claim (True/Mostly True/Half True/Mostly False/False)",
        "Evidence and corrected version for each rated claim",
        "Editor briefing memo with required corrections",
        "Legal risk assessment",
        "Reader-facing correction notice template",
    ],
))
