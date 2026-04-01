"""New employee onboarding plan team — HR & Recruiting."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="onboarding_plan",
    description="Designs a structured 90-day onboarding plan for a new hire with learning milestones, relationship building, and success criteria.",
    category="HR & Recruiting",
    tags=["onboarding", "new hire", "employee experience", "hr", "30-60-90 day plan"],
    agents=[
        AgentSpec(
            name="Day One Designer",
            role="First impressions and logistics specialist",
            instructions=(
                "You are a new hire experience designer. Design the first day: "
                "pre-arrival checklist (hardware, software, accounts, workspace ready), "
                "Day 1 hour-by-hour schedule (who they meet, what they see, what they do), "
                "welcome package contents, "
                "buddy/peer mentor assignment protocol, "
                "manager's first 1-on-1 agenda, "
                "and common first-day anxiety triggers and how to proactively address them."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Learning Architect",
            role="30/60/90 day learning plan specialist",
            instructions=(
                "You are a learning and development specialist. Build a 90-day learning plan: "
                "Week 1: orientation (company, culture, tools, team), "
                "Weeks 2-4: product and domain immersion (what do we build, who do we serve, how), "
                "Month 2: process mastery (how does work get done here, who are the key stakeholders), "
                "Month 3: contribution ramp (first deliverable, first project ownership, first initiative). "
                "For each phase: learning objectives, recommended resources, and knowledge check questions."
            ),
            config=AgentConfig(max_tokens=3500),
        ),
        AgentSpec(
            name="Relationship Mapper",
            role="Stakeholder network building specialist",
            instructions=(
                "You are an organizational dynamics specialist. Produce: "
                "key stakeholder map (who the new hire must build relationships with in 90 days), "
                "coffee chat / informational interview guide (10 questions to learn the organization), "
                "unwritten rules discovery questions (what to ask peers and trusted colleagues), "
                "political landscape navigation guide (decision makers vs. influencers vs. gatekeepers), "
                "and team culture norms to observe and respect."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
        AgentSpec(
            name="Success Criteria Setter",
            role="Performance expectations and feedback loop specialist",
            instructions=(
                "You are a performance management specialist. Create: "
                "30/60/90-day success criteria (specific, measurable goals for each phase), "
                "manager check-in cadence and agenda template, "
                "new hire self-assessment template (how are you feeling, what do you need, where are you stuck?), "
                "end-of-probation review framework, "
                "early warning signs to watch for (signs the new hire is struggling), "
                "and escalation protocol if onboarding is off track."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
    ],
    debate_topics=[
        "Should onboarding prioritize cultural integration or productivity ramp-up?",
        "Culture first (relationships and context before deliverables, longer ramp but higher retention)",
        "Productivity first (contribute quickly to build confidence and demonstrate value)",
        "Parallel tracks (structured learning + small early wins simultaneously)",
    ],
    expected_outputs=[
        "Day 1 hour-by-hour schedule",
        "Pre-arrival logistics checklist",
        "90-day learning plan with phase objectives",
        "Key stakeholder map and coffee chat guide",
        "30/60/90-day success criteria",
        "Manager check-in agenda template",
        "New hire self-assessment template",
        "Early warning signs and escalation protocol",
    ],
))
