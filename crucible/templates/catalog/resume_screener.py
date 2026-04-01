"""Resume screening and candidate evaluation team — HR & Recruiting."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="resume_screener",
    description="Creates a structured resume screening rubric, scorecard, and bias-aware evaluation framework for a hiring process.",
    category="HR & Recruiting",
    tags=["recruiting", "resume screening", "hiring", "candidate evaluation", "scorecard"],
    agents=[
        AgentSpec(
            name="Criteria Designer",
            role="Screening criteria and knockout filter specialist",
            instructions=(
                "You are a structured hiring specialist. Design: "
                "must-have criteria (true knockout filters — absence means immediate reject), "
                "nice-to-have criteria (scored, not knockout), "
                "red flag indicators (job hopping definition for this role, unexplained gaps policy, ATS hack patterns), "
                "and a scoring rubric (1-5 scale for each criterion with behavioral anchors). "
                "Flag any criteria that could introduce disparate impact on protected groups."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Scorecard Builder",
            role="Candidate evaluation scorecard specialist",
            instructions=(
                "You are a hiring process designer. Build: "
                "a structured scorecard with weighted criteria (skills, experience, trajectory, potential), "
                "a calibration guide (sample 'strong yes', 'yes', 'maybe', 'no' profiles for this role), "
                "a side-by-side comparison matrix template for up to 5 finalists, "
                "a bias interrupter checklist (questions to ask yourself before scoring), "
                "and a shortlist decision framework (how to rank when scores are close)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Phone Screen Designer",
            role="Initial screening call structure specialist",
            instructions=(
                "You are an interview process designer. Create: "
                "a 20-30 minute phone screen guide (intro, 5-7 structured questions, time for candidate questions, close), "
                "key probe questions for resume claims that need verification, "
                "motivational qualifier questions (why this role, why now, what are they running toward vs. from?), "
                "compensation and logistics alignment questions, "
                "candidate experience optimization tips, "
                "and a post-call scoring template."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Diversity Auditor",
            role="Equitable screening process specialist",
            instructions=(
                "You are a diversity and equitable hiring specialist. Review the screening process for: "
                "criteria that may screen out underrepresented candidates without being job-relevant, "
                "sourcing gaps that homogenize the funnel before screening begins, "
                "interviewer bias risk in unstructured portions of the process, "
                "name-blind or anonymized resume recommendation, "
                "diverse hiring panel composition guidance, "
                "and metrics to track (funnel conversion by demographic cohort)."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
    ],
    debate_topics=[
        "Should resume screening be structured with a rigid rubric or rely on recruiter judgment?",
        "Structured rubric (reduces bias, enables comparison, scalable, slower per resume)",
        "Experienced recruiter judgment (faster, catches nuance, highly dependent on individual bias)",
        "Hybrid: rubric for knockout filters, judgment for scoring within the band",
    ],
    expected_outputs=[
        "Knockout criteria list",
        "Weighted scoring rubric with behavioral anchors",
        "Calibration guide (strong yes / yes / maybe / no profiles)",
        "Phone screen guide with 7 structured questions",
        "Candidate comparison matrix template",
        "Bias interrupter checklist",
        "Diversity audit with process improvement recommendations",
    ],
))
