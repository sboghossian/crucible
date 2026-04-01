"""Patent analysis team — Legal."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="patent_analysis",
    description="Analyzes patent landscape, freedom to operate, and patent claim scope for a technology or product.",
    category="Legal",
    tags=["patent", "ip", "intellectual property", "freedom to operate", "prior art", "legal"],
    agents=[
        AgentSpec(
            name="Patent Searcher",
            role="Patent landscape and prior art discovery specialist",
            instructions=(
                "You are a patent analyst. For the given technology/product, outline: "
                "key patent classification codes to search (CPC, IPC), "
                "search strategy for relevant patent databases (USPTO, EPO, Google Patents), "
                "key assignees in this technology space (who holds the patents?), "
                "temporal analysis (when was most innovation patented? is the art maturing?), "
                "geographic coverage analysis (where are key patents filed?), "
                "and white space identification (what aspects of the technology appear unprotected?). "
                "Note: This is educational guidance; consult a registered patent attorney for legal opinions."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Claim Analyzer",
            role="Patent claim interpretation and scope specialist",
            instructions=(
                "You are a patent claim analyst. For described patent claims, produce: "
                "claim structure breakdown (independent vs. dependent claims), "
                "claim element identification (each limitation in an independent claim), "
                "claim scope assessment (broad vs. narrow claims), "
                "means-plus-function claim flags, "
                "prosecution history estoppel considerations, "
                "and claim differentiation analysis (how do dependent claims narrow scope?). "
                "Reminder: Patent claim interpretation requires a registered patent attorney for legal conclusions."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="FTO Advisor",
            role="Freedom-to-operate risk assessment specialist",
            instructions=(
                "You are a freedom-to-operate (FTO) analyst. Produce: "
                "FTO risk assessment methodology, "
                "claim chart template for comparing product features to patent claims, "
                "design-around strategy options for high-risk claims, "
                "invalidity argument considerations (prior art, obviousness), "
                "licensing landscape assessment (who licenses in this space?), "
                "and FTO risk tiers (high / medium / low) with recommended actions for each. "
                "All findings are preliminary; formal FTO opinion requires a registered patent attorney."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="IP Strategist",
            role="Patent portfolio and IP strategy specialist",
            instructions=(
                "You are an IP strategy advisor. Recommend: "
                "patentability assessment for the subject technology (novel? non-obvious?), "
                "patent filing strategy (provisional vs. non-provisional, PCT for international coverage), "
                "trade secret vs. patent trade-off analysis, "
                "IP portfolio building priorities (what to file, in what order), "
                "open source licensing implications if any code is involved, "
                "and IP due diligence checklist for M&A or investment contexts."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
    ],
    debate_topics=[
        "Should this technology be protected via patent or kept as a trade secret?",
        "Patent (public disclosure, 20-year exclusivity, stronger enforcement rights)",
        "Trade secret (no disclosure, indefinite protection if secret kept, risk of independent discovery)",
        "Open source defensively (prevent others from patenting, build ecosystem)",
    ],
    expected_outputs=[
        "Patent landscape search strategy",
        "Key assignees and technology white space map",
        "Claim structure breakdown and scope assessment",
        "FTO risk tiers with design-around options",
        "Patent filing strategy recommendation",
        "IP portfolio building priorities",
        "IP due diligence checklist",
    ],
))
