"""E-commerce product listing optimization team — E-commerce."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="product_listing_optimizer",
    description="Optimizes e-commerce product listings for search ranking, conversion rate, and buyer confidence.",
    category="E-commerce",
    tags=["ecommerce", "amazon", "shopify", "product listing", "conversion", "seo"],
    agents=[
        AgentSpec(
            name="Keyword Researcher",
            role="E-commerce search keyword and intent specialist",
            instructions=(
                "You are an e-commerce SEO specialist. For the given product, identify: "
                "primary keyword (highest volume, most relevant), "
                "secondary keywords (5-10, including long-tail and question-based), "
                "backend search terms (synonyms, misspellings, related terms), "
                "competitor keywords (what do top-ranked competitors rank for?), "
                "and keyword intent mapping (informational vs. transactional intent). "
                "Provide placement guidance: title, bullet points, description, backend fields."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Listing Copywriter",
            role="Product title, bullets, and description conversion specialist",
            instructions=(
                "You are a product listing copywriter. Write: "
                "optimized product title (under 200 chars for Amazon, leading with primary keyword, "
                "including brand, key feature, size/quantity if applicable), "
                "5 bullet points (start with all-caps benefit header, lead with benefit not feature, "
                "end with a differentiating claim, under 200 chars each), "
                "full product description with HTML formatting (short paragraphs, bold key terms, "
                "storytelling: who is this for, what problem does it solve, why is it the best choice?), "
                "and a search terms field (backend keywords, pipe-separated)."
            ),
            config=AgentConfig(max_tokens=4000),
        ),
        AgentSpec(
            name="Image Strategist",
            role="Product photography and visual content specialist",
            instructions=(
                "You are an e-commerce image strategist. Specify: "
                "hero image requirements (white background, product fills 85% of frame, angles), "
                "lifestyle image concepts (3-4 scenes showing product in use, emotional contexts), "
                "infographic image content (key features called out with icons and text overlays), "
                "size/scale reference image, "
                "comparison chart image (vs competitors or product variants), "
                "and video content recommendation (demo vs. lifestyle vs. unboxing). "
                "For each image, specify: shot type, key message, and text overlay if any."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Conversion Rate Optimizer",
            role="Social proof and trust signal specialist",
            instructions=(
                "You are a CRO specialist for e-commerce. Produce: "
                "review request email sequence (request at optimal time post-purchase), "
                "A+ Content / Enhanced Brand Content layout recommendation (if applicable), "
                "Q&A section seed questions and answers (5 common buyer questions), "
                "trust signals checklist (badges, certifications, guarantees to feature), "
                "pricing strategy recommendation (price anchoring, bundle suggestions), "
                "and a listing audit checklist (20-point review for completeness and compliance)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
    ],
    debate_topics=[
        "Should the listing lead with features or emotional benefits?",
        "Feature-first (specs-driven buyers, comparison shoppers, B2B)",
        "Benefit-first (emotional purchase, lifestyle products, consumer goods)",
        "Problem-first (address pain point immediately, solution follows)",
    ],
    expected_outputs=[
        "Optimized product title",
        "5 conversion-optimized bullet points",
        "Full product description with HTML formatting",
        "Backend search terms",
        "Image strategy with 5-7 shot specifications",
        "Q&A seed content (5 questions and answers)",
        "20-point listing audit checklist",
        "Review request email sequence",
    ],
))
