"""Tutoring session planner — Education."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="tutoring_session",
    description="Plans and executes a personalized tutoring session with diagnostic, adaptive instruction, and practice problems.",
    category="Education",
    tags=["tutoring", "personalized learning", "1-on-1", "adaptive", "academic support"],
    agents=[
        AgentSpec(
            name="Diagnostic Assessor",
            role="Learning gap and misconception identifier",
            instructions=(
                "You are an educational diagnostician. For the given subject and student profile, produce: "
                "a diagnostic quiz (10 questions spanning prerequisites through target concept), "
                "answer key with diagnostic interpretation (what each wrong answer reveals about misconceptions), "
                "a learning gap map (prerequisite → gap → target skill), "
                "common error patterns for this topic, "
                "and a student profile template to fill in before the session."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Adaptive Instructor",
            role="Personalized explanation and analogy specialist",
            instructions=(
                "You are an expert tutor who adapts explanations to individual learning styles. Produce: "
                "3 different explanations of the core concept (visual-spatial, logical-sequential, story-based), "
                "5 progressively harder worked examples with think-aloud narration, "
                "common mistake walkthroughs (show the wrong approach, identify the error, correct it), "
                "memory aids and mnemonics, "
                "and real-world connection points (why does this matter?)."
            ),
            config=AgentConfig(max_tokens=4000),
        ),
        AgentSpec(
            name="Practice Problem Generator",
            role="Scaffolded practice and mastery builder",
            instructions=(
                "You are a practice problem designer. Generate: "
                "10 scaffolded practice problems (levels 1-3 easy, 4-7 medium, 8-10 challenging), "
                "complete worked solutions for each, "
                "hints for each problem (3 levels of hint: nudge, partial, full), "
                "2 extension problems for advanced students, "
                "and a self-paced practice protocol (how to use these problems independently)."
            ),
            config=AgentConfig(max_tokens=4000),
        ),
        AgentSpec(
            name="Session Planner",
            role="Tutoring session structure and pacing specialist",
            instructions=(
                "You are a tutoring session manager. Design a 60-minute session plan: "
                "minutes 0-5: rapport and goal-setting, "
                "minutes 5-15: diagnostic probe questions (conversational, not a quiz), "
                "minutes 15-35: adaptive instruction sequence based on gap analysis, "
                "minutes 35-50: guided practice with real-time feedback, "
                "minutes 50-60: independent practice problem + wrap-up + next session prep. "
                "Include tutor scripts, student prompts, and pivot strategies if student is lost or bored."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
    ],
    debate_topics=[
        "What instructional sequence will close this student's gap most efficiently?",
        "Address prerequisite gaps first (build from solid foundation)",
        "Teach target concept and fill gaps contextually (motivation-first approach)",
        "Interleaved practice of gap and target skill simultaneously",
    ],
    expected_outputs=[
        "60-minute tutoring session plan",
        "Diagnostic quiz with answer key and error interpretation",
        "3 explanations of core concept (visual, logical, story-based)",
        "10 scaffolded practice problems with solutions and hints",
        "Learning gap map",
        "Tutor scripts and pivot strategies",
        "Between-session homework recommendation",
    ],
))
