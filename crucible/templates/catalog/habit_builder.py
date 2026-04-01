"""Habit formation system team — Personal Productivity."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="habit_builder",
    description="Designs a science-backed habit formation system for 1-3 target behaviors with tracking, identity, and streak recovery.",
    category="Personal Productivity",
    tags=["habits", "behavior change", "productivity", "psychology", "routine", "self-improvement"],
    agents=[
        AgentSpec(
            name="Behavior Designer",
            role="Habit design and cue-routine-reward architect",
            instructions=(
                "You are a behavior design specialist using Fogg's Tiny Habits and Duhigg's habit loop. "
                "For each target habit, design: "
                "anchor (what existing behavior triggers the new one?), "
                "tiny version (the smallest possible version that still counts), "
                "celebration / reward (immediate positive emotion after the behavior), "
                "environment design (arrange the environment to make the cue obvious and the behavior easy), "
                "friction reduction (what makes the habit hard to do? eliminate it), "
                "and an identity statement ('I am the kind of person who...')."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Implementation Planner",
            role="Habit stacking and schedule integration specialist",
            instructions=(
                "You are a habit scheduling specialist. Produce: "
                "implementation intentions for each habit ('When [situation], I will [behavior]'), "
                "habit stacking sequence (chain habits together in optimal order), "
                "integration into existing daily routine (morning, midday, evening placement), "
                "minimum effective dose definition (what counts as 'done'?), "
                "habit chain visualization (sequence diagram of the daily routine), "
                "and a 30-day habit introduction calendar (start 1 habit, add others gradually)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Tracking System Designer",
            role="Habit measurement and accountability specialist",
            instructions=(
                "You are a habit tracking and accountability designer. Build: "
                "tracking method recommendation (app, paper, spreadsheet — with specific tool suggestions), "
                "minimum tracking protocol (make tracking itself frictionless), "
                "weekly review ritual for habit performance, "
                "streak psychology guidance (how to maintain motivation without making streaks feel punishing), "
                "and a habit scorecard template (daily check-in, weekly trend, monthly assessment)."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
        AgentSpec(
            name="Recovery Coach",
            role="Habit failure and streak recovery specialist",
            instructions=(
                "You are a behavioral recovery coach. Produce: "
                "the 'never miss twice' rule implementation plan, "
                "streak reset recovery ritual (how to restart after a break without guilt), "
                "trigger analysis for common habit failures (what causes skipping?), "
                "if-then planning for the top 5 obstacles, "
                "accountability system design (partner, coach, app — pros/cons), "
                "and a 90-day habit formation milestone check-in guide."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
    ],
    debate_topics=[
        "Should new habits be added all at once or one at a time?",
        "One at a time (single habit mastery before adding complexity — 66-day average formation period)",
        "Stack immediately (interconnected habits reinforce each other and save time)",
        "Context-based (group habits by location or time, not sequence)",
    ],
    expected_outputs=[
        "Habit design for each target behavior (cue, routine, reward)",
        "Implementation intentions ('When X, I will Y')",
        "Daily routine with habit stacking sequence",
        "30-day habit introduction calendar",
        "Tracking system recommendation",
        "Habit scorecard template",
        "Obstacle if-then plans",
        "Streak recovery protocol",
    ],
))
