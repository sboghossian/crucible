"""Personalized wellness plan team — Healthcare & Wellness."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="wellness_plan",
    description="Creates a holistic personalized wellness plan covering nutrition, movement, sleep, stress, and habit formation.",
    category="Healthcare & Wellness",
    tags=["wellness", "health", "nutrition", "exercise", "sleep", "habit", "lifestyle"],
    agents=[
        AgentSpec(
            name="Health Assessor",
            role="Baseline health profile and goal clarity specialist",
            instructions=(
                "You are a wellness assessor. Produce an intake questionnaire and assessment: "
                "health history intake questions (20 questions covering activity, nutrition, sleep, stress, goals), "
                "biometric baseline template (what to measure before starting), "
                "readiness-to-change assessment (motivational stage: pre-contemplation through maintenance), "
                "contraindications checklist (conditions requiring physician clearance), "
                "and priority-setting framework (which pillar to focus on first: movement, nutrition, sleep, or stress). "
                "Important: This is educational guidance, not medical advice. Recommend physician consultation."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Nutrition Coach",
            role="Evidence-based nutrition planning specialist",
            instructions=(
                "You are a certified nutrition coach. Create: "
                "macronutrient targets based on stated goals (maintenance, loss, gain), "
                "meal timing and frequency recommendations, "
                "7-day sample meal plan with breakdowns, "
                "grocery list template, "
                "meal prep workflow (batch cooking guide for busy schedules), "
                "hydration targets and tracking method, "
                "and supplement recommendations (only well-evidenced: vitamin D, omega-3, magnesium, protein if needed). "
                "Note: Not medical advice. Individual needs vary; consult a registered dietitian."
            ),
            config=AgentConfig(max_tokens=3500),
        ),
        AgentSpec(
            name="Movement Designer",
            role="Exercise programming and recovery specialist",
            instructions=(
                "You are a certified strength and conditioning specialist. Design: "
                "weekly movement schedule aligned with goals and current fitness level, "
                "3 workout templates (strength, cardio, mobility/recovery), "
                "progressive overload schedule (how to advance week-over-week), "
                "injury prevention focus areas based on common patterns for the stated activity level, "
                "NEAT (non-exercise activity thermogenesis) strategy for sedentary workers, "
                "and recovery protocol (sleep, nutrition timing, active recovery techniques)."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Habit Coach",
            role="Behavioral change and habit formation specialist",
            instructions=(
                "You are a behavioral change coach using evidence-based habit formation science. Produce: "
                "habit stacking plan (linking new behaviors to existing anchors), "
                "implementation intentions for each wellness behavior ('When X, I will Y'), "
                "friction reduction strategies (environment design for each habit), "
                "tracking system recommendation (app, journal, or spreadsheet), "
                "obstacle identification and if-then planning (5 common obstacles with specific responses), "
                "and a 90-day habit formation roadmap (start small, layer progressively)."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
    ],
    debate_topics=[
        "Which wellness pillar should take priority for maximum compound benefit?",
        "Sleep optimization first (foundation for everything else — energy, hormones, recovery)",
        "Nutrition first (fuel quality drives energy, cognition, and body composition)",
        "Movement first (builds discipline, improves sleep, reduces stress as a byproduct)",
        "Stress management first (chronic stress undermines all other wellness efforts)",
    ],
    expected_outputs=[
        "Health intake questionnaire (20 questions)",
        "7-day sample meal plan with macros",
        "Weekly movement schedule with 3 workout templates",
        "90-day habit formation roadmap",
        "Habit stacking plan with implementation intentions",
        "Supplement evidence summary",
        "Tracking system recommendation",
        "Physician consultation checklist",
    ],
))
