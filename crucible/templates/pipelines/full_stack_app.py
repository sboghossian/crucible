"""full_stack_app pipeline: Product Spec → API Service → Web App → Mobile App → Monitoring Setup."""

from . import _register
from ..composer import PipelineBuilder

_register(
    PipelineBuilder(
        "full_stack_app",
        description=(
            "Full-stack application pipeline: defines the product, designs the API, "
            "builds the web frontend, generates the mobile app, and sets up monitoring."
        ),
    )
    .then(
        "product_spec",
        debate_gate=True,
        gate_topic=(
            "Is the product specification sufficiently detailed to drive consistent "
            "API, web, and mobile implementations? "
            "Options: proceed or halt."
        ),
    )
    .then("api_service")
    .then("web_app")
    .then("mobile_app")
    .then("monitoring_setup")
    .build()
)
