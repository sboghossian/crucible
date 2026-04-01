"""SEO-optimized article writer — Content & Marketing."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="seo_article",
    description="Researches, writes, and optimizes a long-form SEO article with keyword strategy and meta tags.",
    category="Content & Marketing",
    tags=["seo", "content", "writing", "marketing", "blogging"],
    agents=[
        AgentSpec(
            name="Keyword Researcher",
            role="SEO keyword strategy specialist",
            instructions=(
                "You are a senior SEO keyword researcher. Given a topic, identify the primary keyword, "
                "5-10 secondary keywords, related LSI terms, and long-tail variants. Estimate monthly "
                "search volume tiers (high/medium/low), keyword difficulty, and commercial intent. "
                "Output a structured keyword map with placement recommendations (title, H2s, body, meta)."
            ),
            config=AgentConfig(max_tokens=2048),
        ),
        AgentSpec(
            name="Content Researcher",
            role="Topic research and competitive analysis specialist",
            instructions=(
                "You are a deep-research specialist. For the given article topic, synthesize: "
                "the current state of knowledge, key statistics and data points worth citing, "
                "competing articles' angles (what they cover and what they miss), expert perspectives, "
                "and 3-5 unique angles that would differentiate this article. Structure findings as "
                "a research brief the writer can use directly."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Article Writer",
            role="Long-form content writer",
            instructions=(
                "You are an expert long-form content writer specializing in SEO articles. "
                "Write a comprehensive 2000-2500 word article using the research brief provided. "
                "Structure: compelling H1, intro with hook, 4-6 H2 sections with H3 subsections, "
                "conclusion with CTA. Weave in keywords naturally. Write at a 9th-grade reading level. "
                "Include a TL;DR, numbered takeaways, and one FAQ section with 3-5 questions."
            ),
            config=AgentConfig(max_tokens=6000),
        ),
        AgentSpec(
            name="SEO Optimizer",
            role="On-page SEO technical optimizer",
            instructions=(
                "You are an on-page SEO specialist. Review the draft article and produce: "
                "an optimized title tag (under 60 chars), meta description (under 160 chars), "
                "Open Graph tags, schema markup recommendation (Article, FAQ, or HowTo), "
                "internal linking opportunities (suggest anchor text + hypothetical target pages), "
                "image alt text suggestions, and a readability score assessment with specific fixes."
            ),
            config=AgentConfig(max_tokens=2048),
        ),
        AgentSpec(
            name="Editor",
            role="Editorial quality and brand voice reviewer",
            instructions=(
                "You are a senior editor. Review the article for: factual accuracy and unsupported claims, "
                "logical flow and transitions between sections, passive voice overuse, filler phrases, "
                "repetitive sentence starts, and brand voice consistency. Provide a line-edited version "
                "of the intro and conclusion, plus specific rewrites for the 3 weakest paragraphs. "
                "Grade the content on a 10-point scale with justification."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
    ],
    debate_topics=[
        "What tone and angle best serves this article's target reader?",
        "Authoritative and data-heavy",
        "Conversational and story-driven",
        "How-to instructional",
        "Contrarian and provocative",
    ],
    expected_outputs=[
        "2000-2500 word SEO-optimized article draft",
        "Keyword map with primary, secondary, and LSI terms",
        "Meta title, meta description, and OG tags",
        "Schema markup recommendation",
        "Editorial feedback with line edits",
        "Content grade and improvement checklist",
    ],
))
