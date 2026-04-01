"""Real estate listing generation team — Real Estate."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="listing_generator",
    description="Generates compelling real estate listing copy, photography direction, and marketing strategy for a property.",
    category="Real Estate",
    tags=["real estate", "listing", "copywriting", "property marketing", "mls"],
    agents=[
        AgentSpec(
            name="Property Storyteller",
            role="Listing copywriting and emotional appeal specialist",
            instructions=(
                "You are a luxury real estate copywriter. Write: "
                "MLS headline (under 50 chars, lead with the most compelling feature), "
                "MLS description (250-300 words: open with an emotional hook, "
                "describe the lifestyle this home enables, highlight top 5 features, "
                "close with neighborhood and location assets), "
                "long-form marketing description (500 words for property website), "
                "3 social media caption variants (Instagram, Facebook, LinkedIn), "
                "and email subject line options for the listing announcement (5 variants)."
            ),
            config=AgentConfig(max_tokens=3500),
        ),
        AgentSpec(
            name="Photography Director",
            role="Real estate photography and visual marketing specialist",
            instructions=(
                "You are a real estate photography director. Produce: "
                "shot list for interior photography (room by room, with styling notes and angles), "
                "exterior shot list (curb appeal, dusk/twilight shoot recommendation), "
                "aerial/drone shot recommendations (if applicable), "
                "virtual staging recommendations for vacant spaces, "
                "video tour script (2-3 minute walkthrough narration), "
                "and floor plan presentation recommendation."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Marketing Strategist",
            role="Property marketing channel and buyer targeting specialist",
            instructions=(
                "You are a real estate marketing strategist. Design: "
                "target buyer profile (demographics, life stage, income, motivation), "
                "multi-channel marketing plan (MLS, Zillow/Redfin, social ads, email, open house), "
                "open house strategy (timing, staging, hospitality elements, follow-up sequence), "
                "digital advertising plan (Facebook/Instagram ad targeting, Google display), "
                "print marketing collateral list (flyer, postcard, brochure), "
                "and a 30-day launch timeline with milestones."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Pricing Advisor",
            role="Comparative market analysis and pricing strategy specialist",
            instructions=(
                "You are a real estate pricing advisor. Produce: "
                "CMA framework (5 comparable sales criteria: proximity, size, age, condition, sale date), "
                "price per square foot analysis, "
                "pricing strategy recommendation (sharp list price vs. list high and negotiate), "
                "offer timeline expectation (days on market target), "
                "price reduction trigger points (if not in contract by day X, reduce by Y%), "
                "and concession strategy (what to offer vs. hold firm on in negotiations)."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
    ],
    debate_topics=[
        "What pricing strategy maximizes final sale price and minimizes days on market?",
        "Price at market (attract broad interest, fast close, full market value)",
        "Price slightly below market (create bidding war, sell above ask)",
        "Price above market (room to negotiate, but risk of stigmatization if it sits)",
    ],
    expected_outputs=[
        "MLS headline and description (250-300 words)",
        "Long-form property website description (500 words)",
        "Social media captions (Instagram, Facebook, LinkedIn)",
        "Photography shot list by room",
        "Video tour script",
        "30-day marketing launch timeline",
        "Target buyer profile",
        "Pricing strategy recommendation",
    ],
))
