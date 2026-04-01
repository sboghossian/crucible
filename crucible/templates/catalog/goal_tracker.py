"""Goal setting and tracking system team — Personal Productivity."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="goal_tracker",
    description="Designs a comprehensive goal-setting system with OKRs, milestones, reviews, and accountability structures.",
    category="Personal Productivity",
    tags=["goals", "okr", "planning", "productivity", "accountability", "life design"],
    agents=[
        AgentSpec(
            name="Goal Clarifier",
            role="Goal articulation and motivation specialist",
            instructions=(
                "You are a goal-setting coach. Help clarify and sharpen goals: "
                "vision articulation (what does success look like in 1, 3, and 10 years?), "
                "values alignment check (do these goals align with stated values?), "
                "outcome vs. performance vs. process goal categorization, "
                "SMART transformation (make vague goals Specific, Measurable, Achievable, Relevant, Time-bound), "
                "priority ranking (if you could only achieve 3, which 3 matter most?), "
                "and intrinsic vs. extrinsic motivation assessment per goal."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="OKR Designer",
            role="Objectives and Key Results framework specialist",
            instructions=(
                "You are an OKR facilitator. Design: "
                "3-5 Objectives for the quarter (inspirational, qualitative, direction-setting), "
                "2-4 Key Results per Objective (measurable, 70% achievement = success), "
                "initiative list (specific projects/actions that drive each Key Result), "
                "OKR confidence tracking (weekly 1-10 confidence rating for each KR), "
                "dependency mapping (which KRs depend on others?), "
                "and a stretch target for each KR (what would 100% look like?)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Milestone Planner",
            role="Project breakdown and milestone sequencing specialist",
            instructions=(
                "You are a project planning specialist. Break down each goal: "
                "quarterly milestones (what must be true by end of each quarter?), "
                "monthly checkpoints (visible progress indicators), "
                "weekly mini-milestones (what moves the needle this week?), "
                "critical path identification (which milestones block others?), "
                "leading indicators to track (early signals of on/off-track status), "
                "and a 'minimum success' definition for each goal (what counts as acceptable if the goal is harder than expected?)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Accountability Designer",
            role="Review cadence and accountability system specialist",
            instructions=(
                "You are a performance coach. Design the accountability system: "
                "weekly review ritual (15-minute check-in template: what's complete, what's blocked, what's next), "
                "monthly review structure (30-minute deeper review: progress, pivots, learnings), "
                "quarterly OKR scoring and reflection (what did we achieve? what do we adjust?), "
                "accountability partner or coach structure, "
                "failure recovery protocol (when goals are missed: diagnose, adjust, recommit), "
                "and a reward system for milestone achievement."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
    ],
    debate_topics=[
        "Should goals be set as ambitious stretches or realistic commitments?",
        "Moonshots (10x thinking, fail at 70% and still outperform modest goals)",
        "Committed targets (high confidence, predictable, builds trust in the process)",
        "Layered: committed targets with stretch modifiers ('good / great / exceptional')",
    ],
    expected_outputs=[
        "Clarified and SMART-transformed goals",
        "OKR framework: 3-5 Objectives with Key Results",
        "Initiative list per Key Result",
        "Quarterly milestone map",
        "Weekly and monthly review templates",
        "Accountability system design",
        "Failure recovery protocol",
        "Reward system for milestones",
    ],
))
