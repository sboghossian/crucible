"""Market research and competitive intelligence team — Research & Analysis."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="market_research",
    description="Produces a comprehensive market research report with competitive landscape, TAM/SAM/SOM analysis, and strategic recommendations.",
    category="Research & Analysis",
    tags=["market research", "competitive analysis", "tam", "strategy", "business intelligence"],
    agents=[
        AgentSpec(
            name="Market Analyst",
            role="Market sizing and dynamics specialist",
            instructions=(
                "You are a senior market analyst. For the given market or product category, produce: "
                "TAM/SAM/SOM calculations with methodology explained, "
                "market growth rate (historical + projected, CAGR), "
                "key market segments and their relative sizes, "
                "demand drivers and inhibitors, "
                "regulatory and macroeconomic factors, "
                "geographic breakdowns (which regions are growing fastest), "
                "and market maturity assessment (emerging, growth, mature, declining)."
            ),
            config=AgentConfig(max_tokens=3500),
        ),
        AgentSpec(
            name="Competitor Scanner",
            role="Competitive landscape and positioning analyst",
            instructions=(
                "You are a competitive intelligence specialist. For the given market, identify: "
                "top 5-8 competitors with funding, revenue estimates, headcount, and founding year, "
                "each competitor's positioning statement and target customer, "
                "feature comparison matrix (top 10 features across all players), "
                "pricing model comparison, "
                "strength/weakness assessment for each, "
                "recent strategic moves (product launches, acquisitions, partnerships, funding), "
                "and white space analysis — what are incumbents NOT doing well?"
            ),
            config=AgentConfig(max_tokens=4000),
        ),
        AgentSpec(
            name="Customer Researcher",
            role="Buyer persona and customer need specialist",
            instructions=(
                "You are a customer research specialist. Produce: "
                "3 detailed buyer personas (demographics, psychographics, goals, pain points, buying triggers, objections), "
                "customer journey map for the primary persona (awareness → consideration → decision → retention), "
                "Jobs-to-be-Done analysis (what is the customer really hiring this product to do?), "
                "voice-of-customer themes (synthesized from publicly available reviews, forums, Reddit), "
                "and willingness-to-pay analysis with price sensitivity indicators."
            ),
            config=AgentConfig(max_tokens=3500),
        ),
        AgentSpec(
            name="Report Writer",
            role="Executive research report synthesizer",
            instructions=(
                "You are a management consulting report writer. Synthesize all findings into: "
                "executive summary (1 page, decision-ready), "
                "key findings section (5-7 headline insights with supporting data), "
                "strategic implications and recommended market entry or positioning approach, "
                "risk matrix (market, competitive, regulatory, execution risks), "
                "and a 'Questions This Research Raises' section to guide further investigation. "
                "Format for a C-suite audience: clear, visual where possible (tables, bullet matrices), no filler."
            ),
            config=AgentConfig(max_tokens=4000),
        ),
    ],
    debate_topics=[
        "What research methodology provides the highest signal-to-noise ratio for this market?",
        "Primary quantitative research (surveys, structured interviews at scale)",
        "Secondary desk research (analyst reports, SEC filings, job postings, web scraping)",
        "Qualitative in-depth interviews with 10-15 target customers",
        "Hybrid: secondary research to frame, qualitative to validate",
    ],
    expected_outputs=[
        "TAM/SAM/SOM analysis with methodology",
        "Competitive landscape with feature comparison matrix",
        "3 buyer personas with Jobs-to-be-Done analysis",
        "Customer journey map",
        "White space and opportunity analysis",
        "Risk matrix",
        "Executive summary (decision-ready)",
        "Strategic recommendations",
    ],
))
