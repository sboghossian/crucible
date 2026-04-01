"""Exam preparation team — Education."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="exam_prep",
    description="Creates a personalized exam preparation plan with study schedule, practice tests, and spaced repetition strategy.",
    category="Education",
    tags=["exam prep", "studying", "test prep", "sat", "gre", "bar exam", "certification"],
    agents=[
        AgentSpec(
            name="Exam Analyst",
            role="Exam structure and high-yield topic identifier",
            instructions=(
                "You are an exam preparation strategist. For the given exam, analyze: "
                "exam format (question types, timing, scoring), "
                "topic weight distribution (which sections carry the most points?), "
                "historically high-yield topics (what comes up most often?), "
                "common traps and question patterns, "
                "passing score requirements and percentile context, "
                "and available official practice resources."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Study Plan Architect",
            role="Personalized study schedule and resource strategist",
            instructions=(
                "You are a study plan architect. Given the exam date and student's current level, build: "
                "a week-by-week study schedule from today to exam day, "
                "daily session structure (what to study, for how long, in what order), "
                "spaced repetition schedule for vocabulary/formulas/facts, "
                "practice test schedule (when to take full-length tests, when to review), "
                "resource recommendation (books, apps, videos, question banks) with time allocation, "
                "and contingency plans for weeks where progress falls behind."
            ),
            config=AgentConfig(max_tokens=3500),
        ),
        AgentSpec(
            name="Practice Test Generator",
            role="Mock exam and question bank specialist",
            instructions=(
                "You are a test item writer. Create: "
                "20 practice questions spanning the exam's major topic areas, "
                "with difficulty distribution matching the real exam (easy/medium/hard), "
                "detailed answer explanations for each question (why right is right, why wrong is wrong), "
                "time benchmarks per question type, "
                "and a scoring guide with performance interpretation (what your score predicts)."
            ),
            config=AgentConfig(max_tokens=5000),
        ),
        AgentSpec(
            name="Performance Coach",
            role="Test-taking strategy and anxiety management specialist",
            instructions=(
                "You are a high-performance exam coach. Provide: "
                "question-type specific strategies (multiple choice elimination, reading comp tactics, essay timing), "
                "time management system for the exam day, "
                "educated guessing frameworks for when stuck, "
                "test anxiety management techniques (breathing, reframing, pre-exam routine), "
                "exam day logistics checklist (what to bring, what to eat, when to arrive), "
                "and a mental model for approaching unfamiliar questions."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
    ],
    debate_topics=[
        "What study strategy produces the highest score gain per hour of study time?",
        "Passive review (re-reading, highlighting, watching lectures)",
        "Active recall (flashcards, practice problems, self-testing without notes)",
        "Interleaved practice (mix topics rather than block-studying one at a time)",
        "Deliberate practice (focus exclusively on weak areas, not strengths)",
    ],
    expected_outputs=[
        "Week-by-week study schedule to exam day",
        "High-yield topic priority list",
        "20 practice questions with detailed explanations",
        "Spaced repetition schedule for key facts",
        "Test-taking strategy guide",
        "Exam day logistics checklist",
        "Performance prediction based on practice scores",
    ],
))
