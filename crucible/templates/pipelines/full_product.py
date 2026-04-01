"""full_product pipeline: Market Research → Product Spec → Web App → Codebase Audit → Course Creator."""

from . import _register
from ..composer import PipelineBuilder

_register(
    PipelineBuilder(
        "full_product",
        description=(
            "End-to-end product development pipeline: validates the market, defines the product, "
            "generates the web app, audits the codebase, and produces a training course."
        ),
    )
    .then(
        "market_research",
        debate_gate=True,
        gate_topic=(
            "Is there sufficient market opportunity to justify building this product? "
            "Options: proceed (strong opportunity) or halt (insufficient demand)."
        ),
    )
    .then(
        "product_spec",
        debate_gate=True,
        gate_topic=(
            "Is the product spec clear and scoped enough to begin development? "
            "Options: proceed (spec is actionable) or halt (too vague / too broad)."
        ),
    )
    .then("web_app")
    .then(
        "codebase_audit",
        debate_gate=False,
    )
    .then("course_creator")
    .build()
)
