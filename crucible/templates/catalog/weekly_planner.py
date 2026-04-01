"""Weekly personal planning team — Personal Productivity."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="weekly_planner",
    description="Plans an effective, prioritized, and energy-optimized week aligned with goals and constraints.",
    category="Personal Productivity",
    tags=["productivity", "planning", "weekly review", "time management", "goals"],
    agents=[
        AgentSpec(
            name="Weekly Reviewer",
            role="Past week reflection and learning specialist",
            instructions=(
                "You are a weekly review coach. Facilitate a structured review of the past week: "
                "wins accomplished (what went well?), "
                "misses and what they reveal (what didn't happen and why?), "
                "time audit (where did time actually go vs. where it was planned to go?), "
                "energy pattern analysis (when were you most and least effective?), "
                "commitments not kept and recovery plan, "
                "key learning from the week, "
                "and what would make next week feel like a success?"
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Priority Setter",
            role="Goal alignment and priority clarification specialist",
            instructions=(
                "You are a strategic prioritization coach. For the coming week, define: "
                "the 3 most important outcomes to achieve (MIT — Most Important Tasks), "
                "alignment check: do this week's priorities advance quarterly or annual goals?, "
                "must-do vs. should-do vs. nice-to-do categorization for all pending tasks, "
                "decision on what to deliberately NOT do this week (strategic subtraction), "
                "and the single 'if I only get one thing done this week' priority."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
        AgentSpec(
            name="Schedule Architect",
            role="Time blocking and calendar optimization specialist",
            instructions=(
                "You are a calendar design specialist. Build the weekly schedule: "
                "time block assignments for the 3 MITs (protect the best energy time), "
                "meeting audit (which scheduled meetings are necessary? which can be async?), "
                "buffer and transition time allocation (no back-to-back blocks all day), "
                "energy management (deep work in peak hours, admin in low-energy slots), "
                "weekly anchor habits (morning routine, end-of-day shutdown, exercise), "
                "and a daily startup routine to enter each day with clarity."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Resilience Planner",
            role="Obstacle anticipation and contingency planning specialist",
            instructions=(
                "You are a planning resilience coach. Produce: "
                "anticipated obstacles and if-then responses ('If X interrupts, I will Y'), "
                "buffer tasks (productive work to do when a meeting cancels or time appears), "
                "energy management plan (what to do when motivation drops mid-week?), "
                "communication commitments for the week (who needs to hear from you, about what?), "
                "and an end-of-week shutdown ritual to process the week completely."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
    ],
    debate_topics=[
        "What time management philosophy should govern this week's planning?",
        "Time blocking (every hour has a job, maximum control and structure)",
        "Task batching (group similar work, minimize context switching)",
        "Energy management over time management (match task type to energy state)",
        "Agile sprints (commit to a sprint backlog, protect it from scope creep)",
    ],
    expected_outputs=[
        "Past week reflection summary",
        "3 Most Important Tasks for the week",
        "Time-blocked weekly schedule",
        "Meeting audit and async alternatives",
        "If-then obstacle responses",
        "Daily startup routine",
        "End-of-week shutdown ritual",
    ],
))
