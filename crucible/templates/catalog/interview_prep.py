"""Interview preparation team (for candidates) — HR & Recruiting."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="interview_prep",
    description="Prepares a job candidate for interviews with company research, behavioral questions, technical prep, and salary negotiation.",
    category="HR & Recruiting",
    tags=["interview prep", "job search", "career", "salary negotiation", "behavioral interview"],
    agents=[
        AgentSpec(
            name="Company Researcher",
            role="Company and role intelligence specialist",
            instructions=(
                "You are a company research specialist. For the given company and role, produce: "
                "company overview (business model, revenue, size, stage, recent news), "
                "products and competitive position, "
                "company culture signals (Glassdoor themes, LinkedIn posts, public statements), "
                "interviewer LinkedIn research guide (how to research your interviewers professionally), "
                "the role's likely business impact and team context, "
                "and 5 insightful questions the candidate should ask at the end of the interview."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Behavioral Coach",
            role="STAR method and behavioral interview specialist",
            instructions=(
                "You are a behavioral interview coach. Prepare: "
                "12 STAR-format story templates covering: leadership, conflict, failure, achievement, "
                "collaboration, ambiguity, initiative, influence without authority, feedback received, "
                "customer focus, prioritization, and innovation. "
                "For each story: situation, task, action (most detail here), result (quantified where possible), "
                "and the core competency it demonstrates. "
                "Include anti-patterns to avoid (rambling, blaming others, using 'we' exclusively)."
            ),
            config=AgentConfig(max_tokens=5000),
        ),
        AgentSpec(
            name="Technical Prep Coach",
            role="Technical assessment and skills demonstration specialist",
            instructions=(
                "You are a technical interview coach. Based on the role requirements, produce: "
                "likely technical assessment topics and formats, "
                "10 practice technical questions with model answers, "
                "live coding / whiteboard strategy (how to think out loud, handle being stuck), "
                "take-home assignment approach (structure, time management, presentation), "
                "common technical red flags and how to avoid them, "
                "and resources for any skill gaps to address before the interview."
            ),
            config=AgentConfig(max_tokens=3500),
        ),
        AgentSpec(
            name="Salary Negotiator",
            role="Compensation negotiation and offer evaluation specialist",
            instructions=(
                "You are a salary negotiation coach. Produce: "
                "market compensation range research framework (how to find reliable data), "
                "compensation components to evaluate beyond base salary (bonus, equity, benefits, PTO), "
                "BATNA analysis (what is the candidate's best alternative?), "
                "negotiation script (how to counter an offer professionally and confidently), "
                "common negotiation objections and responses, "
                "offer evaluation scorecard (total compensation + culture + growth + risk), "
                "and decision framework for comparing multiple offers."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
    ],
    debate_topics=[
        "Should the candidate lead with passion for the company or demonstrate hard skills first?",
        "Lead with passion and company fit (emotional connection, cultural alignment)",
        "Lead with hard skills and results (de-risk the hire first, then differentiate on fit)",
        "Lead with the problem the role solves (show business acumen immediately)",
    ],
    expected_outputs=[
        "Company research brief",
        "5 insightful questions to ask the interviewer",
        "12 STAR-format behavioral stories",
        "10 technical practice questions with model answers",
        "Salary negotiation script",
        "Offer evaluation scorecard",
        "Decision framework for multiple offers",
    ],
))
