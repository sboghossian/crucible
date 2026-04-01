"""Customer review analysis team — E-commerce."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="customer_review_analysis",
    description="Analyzes customer reviews to extract sentiment, themes, product improvement opportunities, and marketing angles.",
    category="E-commerce",
    tags=["reviews", "sentiment analysis", "voice of customer", "product feedback", "nps"],
    agents=[
        AgentSpec(
            name="Sentiment Analyzer",
            role="Review sentiment and rating distribution specialist",
            instructions=(
                "You are a sentiment analysis specialist. Given customer reviews, produce: "
                "overall sentiment score (positive / neutral / negative %) per star rating band, "
                "sentiment trend (improving, stable, declining over time), "
                "most emotionally charged phrases (top 20 positive and top 20 negative), "
                "verified purchaser vs. all-reviewer sentiment gap, "
                "and platform-by-platform sentiment comparison (Amazon vs. website vs. social)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Theme Extractor",
            role="Review topic clustering and insight specialist",
            instructions=(
                "You are a qualitative research analyst. From the review corpus, extract: "
                "top 10 mentioned themes (features, issues, use cases) with frequency and sentiment, "
                "unexpected use cases customers discovered, "
                "comparison mentions (what competitors do customers compare this to?), "
                "gift purchase patterns, "
                "return reason themes (from negative reviews), "
                "and 'hidden gem' insights — what customers love that isn't featured in the listing?"
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Product Improvement Advisor",
            role="Product feedback and iteration specialist",
            instructions=(
                "You are a product improvement advisor. From review themes, identify: "
                "top 5 product improvement opportunities ranked by complaint frequency × impact, "
                "quick wins vs. major R&D investments, "
                "packaging and unboxing experience feedback, "
                "size/color/variant requests, "
                "warranty and support experience themes, "
                "and a 'what would make this a 5-star product?' synthesis from 3-4 star reviewers."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Marketing Copywriter",
            role="Review-derived marketing and social proof specialist",
            instructions=(
                "You are a marketing copywriter who mines customer reviews for authentic copy. Produce: "
                "10 review quotes suitable for marketing (with paraphrase if needed for clarity), "
                "3 customer success story outlines (drawn from 5-star reviews), "
                "FAQ content from repeated review questions, "
                "testimonial email sequence for post-purchase review solicitation, "
                "and social proof placement strategy (which quotes go on homepage, PDP, ads)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
    ],
    debate_topics=[
        "What is the #1 priority: fix the most complained-about issues, or amplify what customers love?",
        "Fix negatives first (prevent 1-3 star reviews that tank conversion rate)",
        "Amplify positives (double down on what's working, attract more of the right customers)",
        "Balanced approach (patch critical defects, market verified strengths)",
    ],
    expected_outputs=[
        "Overall sentiment report by star rating band",
        "Top 10 review themes with frequency and sentiment",
        "Top 5 product improvement opportunities",
        "10 marketing-ready customer quotes",
        "3 customer success story outlines",
        "FAQ content derived from reviews",
        "Review solicitation email sequence",
    ],
))
