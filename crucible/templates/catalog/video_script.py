"""Video script and production team — Creative."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="video_script",
    description="Produces a complete video script with storyboard, shot list, and production notes for YouTube, course, or ad content.",
    category="Creative",
    tags=["video", "script", "youtube", "storyboard", "production", "content creation"],
    agents=[
        AgentSpec(
            name="Content Researcher",
            role="Topic depth and audience interest researcher",
            instructions=(
                "You are a video content researcher. For the given video topic, produce: "
                "audience intent analysis (why are people searching for this?), "
                "top 5 competing videos on this topic — what they cover, what they miss, "
                "unique angles that would differentiate this video, "
                "key statistics and surprising facts that create 'wow' moments, "
                "expert perspectives worth citing, "
                "and SEO considerations for the video title, description, and tags."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Scriptwriter",
            role="Video script specialist",
            instructions=(
                "You are a professional YouTube and video scriptwriter. Write a complete script: "
                "hook (first 15 seconds — pattern interrupt, bold claim, or compelling question), "
                "intro (who this is for, what they'll learn, why trust you), "
                "body sections (3-5 main points, each with story/example/data/application), "
                "transitions between sections, "
                "CTA section, "
                "outro (subscribe, next video, comment prompt). "
                "Mark [B-ROLL: description] throughout. Include speaker notes for tone/emphasis."
            ),
            config=AgentConfig(max_tokens=5000),
        ),
        AgentSpec(
            name="Storyboarder",
            role="Visual narrative and shot composition specialist",
            instructions=(
                "You are a video storyboard artist. Convert the script into: "
                "scene-by-scene storyboard descriptions (what's on screen for each beat), "
                "B-roll shot list with descriptions (locations, subjects, camera movement), "
                "motion graphics and text overlay suggestions, "
                "thumbnail concept (main element, text overlay, color scheme, emotion), "
                "and a visual pacing guide (when to cut, when to hold, when to use slow motion)."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Production Director",
            role="Production logistics and quality specialist",
            instructions=(
                "You are a video production director. Produce: "
                "pre-production checklist (what to prepare, gather, and test before filming), "
                "filming setup guide (camera settings, lighting setup, audio setup), "
                "teleprompter / notes setup recommendation, "
                "post-production editing guide (cut points, music selection, color grade recommendation), "
                "chapter timestamps for YouTube, "
                "and a YouTube SEO package: optimized title (under 60 chars), "
                "first 150-char description hook, full description template, and tag set."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
    ],
    debate_topics=[
        "What narrative structure maximizes audience retention for this topic?",
        "Problem-agitate-solve (lead with pain, build tension, deliver relief)",
        "Story-first (open with a narrative hook, weave in information)",
        "Listicle format (numbered structure, satisfying checkpoints)",
        "Tutorial / step-by-step (procedural, high rewatch value)",
    ],
    expected_outputs=[
        "Full video script with speaker notes",
        "Hook options (3 variants)",
        "Scene-by-scene storyboard",
        "B-roll shot list",
        "Thumbnail concept brief",
        "Filming and production checklist",
        "YouTube SEO package (title, description, tags)",
        "Chapter timestamps",
    ],
))
