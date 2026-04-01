"""Social media campaign planner — Content & Marketing."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="social_media_campaign",
    description="Plans a multi-platform social media campaign with content calendar, platform-specific posts, and scheduling strategy.",
    category="Content & Marketing",
    tags=["social media", "campaign", "content calendar", "marketing", "instagram", "linkedin", "twitter"],
    agents=[
        AgentSpec(
            name="Trend Analyst",
            role="Social media trend and audience intelligence specialist",
            instructions=(
                "You are a social media trend analyst. For the given campaign topic, analyze: "
                "current trending hashtags and content formats per platform (Instagram Reels, LinkedIn Articles, "
                "X/Twitter threads, TikTok, YouTube Shorts), target audience psychographics and pain points, "
                "competitor campaign benchmarks, optimal content types (video, carousel, static, text), "
                "and seasonal/cultural timing considerations. Output a trend brief with data-backed recommendations."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Content Creator",
            role="Multi-format social media copywriter",
            instructions=(
                "You are a social media copywriter. Create platform-native content for: "
                "Instagram (3 carousel caption sets, 2 Reel scripts, 5 Story slides), "
                "LinkedIn (2 long-form posts + 1 poll), "
                "X/Twitter (3 thread starters with 5-tweet threads each), "
                "TikTok/YouTube Shorts (2 script outlines with hook, body, CTA). "
                "Each piece must have a hook, body, CTA, and hashtag set. Match platform voice."
            ),
            config=AgentConfig(max_tokens=6000),
        ),
        AgentSpec(
            name="Platform Strategist",
            role="Channel strategy and audience growth specialist",
            instructions=(
                "You are a platform strategist. Define for each platform: "
                "target audience segment, content pillars (3 per platform), "
                "posting frequency and best times (with timezone guidance), "
                "engagement tactics (questions, polls, challenges, collabs), "
                "paid amplification recommendations (budget % per platform, ad format), "
                "and KPIs to track (reach, engagement rate, follower growth, link clicks). "
                "Justify every platform inclusion or exclusion."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Content Calendar Builder",
            role="Editorial calendar and scheduling specialist",
            instructions=(
                "You are an editorial calendar specialist. Build a 4-week content calendar with: "
                "date, platform, content type, caption/script reference, visual direction, "
                "hashtags, and CTA for every post slot. Format as a Markdown table. "
                "Include a launch day timeline (T-7 through T+7), a content batching guide, "
                "and a repurposing matrix showing how each piece can be adapted across platforms."
            ),
            config=AgentConfig(max_tokens=4000),
        ),
    ],
    debate_topics=[
        "Which platform should receive the majority of campaign budget and effort?",
        "Instagram (visual storytelling and Reels reach)",
        "LinkedIn (B2B authority and organic reach)",
        "TikTok (viral potential and Gen Z reach)",
        "X/Twitter (real-time conversation and thought leadership)",
    ],
    expected_outputs=[
        "4-week content calendar with post-by-post breakdown",
        "Platform-native copy for Instagram, LinkedIn, X, TikTok",
        "Hashtag sets per platform and content type",
        "Posting schedule with optimal times",
        "Paid amplification budget recommendations",
        "Campaign KPI dashboard template",
        "Content repurposing matrix",
    ],
))
