"""Sales cold outreach sequence team — Sales."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="cold_outreach_sequence",
    description="Builds a multi-touch cold outreach sequence for B2B sales with personalized email, LinkedIn, and call scripts.",
    category="Sales",
    tags=["sales", "outreach", "email sequence", "cold email", "b2b", "sdr", "prospecting"],
    agents=[
        AgentSpec(
            name="ICP Researcher",
            role="Ideal customer profile and prospect intelligence specialist",
            instructions=(
                "You are a B2B sales researcher. Define and research: "
                "Ideal Customer Profile (ICP) for this product/service (firmographics, technographics, behavioral triggers), "
                "buyer personas within the ICP (economic buyer, champion, influencer, gatekeeper), "
                "trigger events to prioritize (funding, hiring, product launch, regulation, expansion), "
                "personalization signals to use in outreach (LinkedIn activity, company news, job postings), "
                "and an account prioritization framework (Tier 1 / Tier 2 / Tier 3 criteria)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Email Copywriter",
            role="Cold email sequence specialist",
            instructions=(
                "You are a B2B cold email expert. Write a 5-touch email sequence: "
                "Email 1 (Day 1): personalized opener, one-line value prop, soft CTA (question, not meeting ask), "
                "Email 2 (Day 4): different angle, social proof or case study reference, "
                "Email 3 (Day 8): insight or relevant stat that creates urgency, "
                "Email 4 (Day 14): breakup framing ('I'll stop reaching out if not relevant'), "
                "Email 5 (Day 30): evergreen re-engage. "
                "Each email: under 150 words, no attachments, one CTA, strong subject line. "
                "Include 3 subject line variants per email."
            ),
            config=AgentConfig(max_tokens=4000),
        ),
        AgentSpec(
            name="LinkedIn Strategist",
            role="LinkedIn outreach and social selling specialist",
            instructions=(
                "You are a LinkedIn social selling specialist. Design: "
                "LinkedIn connection request note (under 300 chars, personalized), "
                "post-connect message sequence (3 messages: value, insight, ask), "
                "InMail template for non-connections, "
                "LinkedIn content strategy to warm up prospects before cold outreach, "
                "profile optimization checklist for the SDR's profile, "
                "and engagement strategy (comment on prospect posts before reaching out)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Call Script Writer",
            role="Cold call and voicemail script specialist",
            instructions=(
                "You are a cold calling coach. Write: "
                "30-second cold call opener (who you are, why you're calling, hook), "
                "discovery question set (5 questions to qualify and engage), "
                "objection handling scripts for the 5 most common objections "
                "('not interested', 'send me an email', 'we have a vendor', 'no budget', 'not the right person'), "
                "voicemail script (under 20 seconds, compelling enough to return the call), "
                "and meeting confirmation script."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
    ],
    debate_topics=[
        "What channel should anchor the outreach sequence for maximum response rate?",
        "Email-first (scalable, trackable, less intrusive, lower response rate)",
        "LinkedIn-first (social context warms the cold contact, better connection rates)",
        "Phone-first (highest response rate per contact, time-intensive, not scalable)",
        "Multi-channel simultaneously (highest total response, risk of feeling overwhelming)",
    ],
    expected_outputs=[
        "ICP definition and buyer persona map",
        "5-touch email sequence with subject line variants",
        "LinkedIn connection request and message sequence",
        "Cold call opener and objection handling scripts",
        "Voicemail script",
        "Trigger events to monitor for personalization",
        "Account prioritization framework (Tier 1/2/3)",
    ],
))
