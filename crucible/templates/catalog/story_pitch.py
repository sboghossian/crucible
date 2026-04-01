"""Story pitch development team — Media & Journalism."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="story_pitch",
    description="Develops and refines a compelling story pitch for editors, with angle, sources, format, and audience relevance.",
    category="Media & Journalism",
    tags=["journalism", "pitch", "story", "media", "editorial", "narrative"],
    agents=[
        AgentSpec(
            name="Angle Developer",
            role="Story angle and news hook specialist",
            instructions=(
                "You are a story development editor. Sharpen the story angle: "
                "news hook (what makes this timely RIGHT NOW?), "
                "so-what statement (why should the reader care?), "
                "audience specificity (who is this story for — and who is NOT the target reader?), "
                "3 alternative angles (different frames for the same underlying story), "
                "comparable published stories (precedent + differentiation), "
                "and a 50-word pitch sentence that explains the story, the hook, and the stakes."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Source Planner",
            role="Story sources and evidence specialist",
            instructions=(
                "You are an editorial researcher. Identify: "
                "primary sources to interview (people with direct knowledge or experience), "
                "expert voices (academic, industry, independent credibility), "
                "data and documents that would anchor the story, "
                "visual storytelling opportunities (photos, graphics, data visualizations), "
                "access challenges and mitigation strategies, "
                "and a reporting timeline estimate."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
        AgentSpec(
            name="Format Advisor",
            role="Story format and publication strategy specialist",
            instructions=(
                "You are an editorial strategy advisor. Recommend: "
                "ideal format (news article, long-form feature, Q&A, investigation, explainer, data story), "
                "ideal publication (which outlets are most likely to publish this and why?), "
                "ideal length and structure, "
                "multimedia components that would strengthen the story (video, interactive, podcast), "
                "SEO headline options (3 variants) if digital publication, "
                "and a publication exclusivity vs. multi-submission strategy."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
        AgentSpec(
            name="Pitch Writer",
            role="Editor pitch email and narrative hook specialist",
            instructions=(
                "You are a story pitch specialist. Write: "
                "a 300-word pitch email to an editor (hook, angle, why now, your sources, your credentials, format, timeline), "
                "a 50-word elevator pitch for verbal situations, "
                "a logline (one sentence that captures the entire story), "
                "and anticipate 3 common editor rejections with responses "
                "('we covered this recently', 'this isn't our audience', 'we need more exclusivity')."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
    ],
    debate_topics=[
        "Which angle will most compel an editor to assign this story?",
        "News hook (timely peg to a current event or data release)",
        "Human interest (individual story that illuminates a larger trend)",
        "Data-driven (original analysis that reveals something not previously known)",
        "Contrarian (challenges a commonly held belief with evidence)",
    ],
    expected_outputs=[
        "50-word pitch sentence",
        "3 alternative angles",
        "Source plan with reporting timeline",
        "Publication strategy and target outlets",
        "300-word pitch email to editor",
        "SEO headline variants (3 options)",
        "Logline (one sentence)",
        "Editor objection responses",
    ],
))
