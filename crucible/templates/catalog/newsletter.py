"""Newsletter production pipeline — Content & Marketing."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="newsletter",
    description="Curates content, writes, structures, and A/B tests a high-converting email newsletter issue.",
    category="Content & Marketing",
    tags=["newsletter", "email", "content", "copywriting", "a/b testing"],
    agents=[
        AgentSpec(
            name="Content Curator",
            role="Information gatherer and editorial filter",
            instructions=(
                "You are a newsletter content curator. For the given topic and audience, surface: "
                "5-7 most shareable/relevant items from the past week (news, research, tools, opinions), "
                "ranked by relevance and novelty. For each item provide: headline, 2-sentence summary, "
                "why it matters to the audience, and a source reference. Flag evergreen vs time-sensitive content. "
                "Suggest one 'hidden gem' — something the audience likely hasn't seen yet."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Newsletter Writer",
            role="Email copywriter and storyteller",
            instructions=(
                "You are a newsletter writer who writes like a trusted friend with expert knowledge. "
                "Write a complete newsletter issue: opener (personal, hook-driven, 100 words), "
                "3-4 curated items with sharp commentary (not just summaries), "
                "one original insight or mini-essay (300 words), "
                "a 'quick hits' section with 3-5 bullets, "
                "and a closing CTA. Total target: 800-1000 words. "
                "Voice: warm, direct, slightly opinionated, no corporate speak."
            ),
            config=AgentConfig(max_tokens=4000),
        ),
        AgentSpec(
            name="Email Designer",
            role="Email structure and formatting specialist",
            instructions=(
                "You are an email design specialist. For the newsletter draft, provide: "
                "HTML/text structure recommendation (single column vs multi-column), "
                "section dividers and visual hierarchy guidance, "
                "CTA button placement and copy, "
                "preheader text (90 chars max), "
                "mobile rendering checklist, "
                "and estimated read time. Flag any elements likely to trigger spam filters."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
        AgentSpec(
            name="Subject Line A/B Tester",
            role="Email subject line and open rate optimizer",
            instructions=(
                "You are an email subject line specialist. Generate 8 subject line variants: "
                "2 curiosity-gap, 2 direct-value, 2 numbered/list, 2 personalization hooks. "
                "For each, predict open rate impact (low/medium/high) with reasoning, "
                "flag emoji usage, length (under 50 chars is better), and preview text pairings. "
                "Recommend the top 2 for A/B testing and explain the hypothesis. "
                "Also generate 3 preheader text variants to pair with the winning subjects."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
    ],
    debate_topics=[
        "What editorial angle maximizes open rate and reader retention for this issue?",
        "News-forward curation with minimal commentary",
        "Opinion-first with original analysis",
        "Actionable how-to with tools and tactics",
    ],
    expected_outputs=[
        "Full newsletter issue draft (800-1000 words)",
        "Curated content items with editorial commentary",
        "8 subject line variants with A/B test recommendation",
        "3 preheader text options",
        "HTML structure and formatting guidance",
        "Spam filter risk assessment",
        "Estimated read time and mobile rendering checklist",
    ],
))
