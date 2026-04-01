"""startup_launch pipeline: Market Research → Startup Pitch → Financial Model → Legal Review."""

from . import _register
from ..composer import PipelineBuilder

_register(
    PipelineBuilder(
        "startup_launch",
        description=(
            "Startup launch readiness pipeline: validates the market, builds the investor pitch, "
            "models the financials, and reviews legal foundations."
        ),
    )
    .then(
        "market_research",
        debate_gate=True,
        gate_topic=(
            "Does the market research reveal a compelling enough opportunity "
            "to justify building and pitching this startup? "
            "Options: proceed or halt."
        ),
    )
    .then("startup_pitch")
    .then(
        "financial_model",
        debate_gate=True,
        gate_topic=(
            "Do the financial projections show a viable path to profitability "
            "within a reasonable timeframe? "
            "Options: proceed or halt."
        ),
    )
    .then("legal_review")
    .build()
)
