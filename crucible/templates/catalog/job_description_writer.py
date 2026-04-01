"""Job description writing team — HR & Recruiting."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="job_description_writer",
    description="Writes compelling, bias-reduced job descriptions that attract qualified candidates and reflect the role accurately.",
    category="HR & Recruiting",
    tags=["recruiting", "job description", "hiring", "talent", "hr", "diversity"],
    agents=[
        AgentSpec(
            name="Role Analyst",
            role="Job requirements and success criteria specialist",
            instructions=(
                "You are a job analysis specialist. For the given role, produce: "
                "role purpose statement (why does this role exist?), "
                "key responsibilities ranked by time allocation, "
                "success metrics for the first 30/60/90 days, "
                "required vs. preferred qualifications (be ruthless about what's truly required), "
                "tools and technology required, "
                "reporting structure and team context, "
                "and scope of impact (what decisions does this person make or influence?)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Bias Auditor",
            role="Inclusive language and diversity specialist",
            instructions=(
                "You are an inclusive hiring specialist. Review the job description for: "
                "gendered language (aggressive/masculine-coded words that deter women), "
                "age-discriminatory phrases ('recent grad', 'digital native', '5+ years only'), "
                "unnecessary degree requirements (what could be demonstrated by experience instead?), "
                "cultural fit language (often excludes underrepresented groups), "
                "jargon that excludes career changers, "
                "and any EEO compliance issues. "
                "Provide specific rewrites for each flagged phrase."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
        AgentSpec(
            name="Employer Brand Writer",
            role="Candidate attraction and company culture copywriter",
            instructions=(
                "You are an employer brand copywriter. Write: "
                "compelling company overview (3 sentences: what you do, why it matters, what makes it special), "
                "culture and values section (specific, not generic — avoid 'we work hard and play hard'), "
                "benefits and perks section (grouped: health, financial, time off, growth, culture), "
                "remote/hybrid/in-office policy statement, "
                "DEI commitment statement (authentic, not performative), "
                "and a candidate closing CTA (what happens after they apply?)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Distribution Strategist",
            role="Job posting channel and candidate sourcing specialist",
            instructions=(
                "You are a recruiting distribution specialist. Recommend: "
                "job board selection (LinkedIn, Indeed, specialized boards for the role), "
                "social media posting strategy (which platforms, what format, employee amplification), "
                "sourcing channels beyond job boards (communities, conferences, universities, GitHub), "
                "referral program messaging, "
                "and a posting optimization schedule (when to re-boost, how to track source effectiveness)."
            ),
            config=AgentConfig(max_tokens=1500),
        ),
    ],
    debate_topics=[
        "How should required qualifications be structured to maximize qualified applicant pool?",
        "List specific credentials and years of experience (filters for precision, risks missing great candidates)",
        "List outcomes and competencies, not credentials (broader pool, more screening work)",
        "Minimal requirements with strong culture and values emphasis (attract motivation-fit candidates)",
    ],
    expected_outputs=[
        "Complete job description draft",
        "Inclusive language audit with rewrites",
        "Company overview and culture section",
        "Benefits and perks section",
        "DEI commitment statement",
        "Distribution strategy and job board recommendations",
        "First 90-day success criteria",
    ],
))
