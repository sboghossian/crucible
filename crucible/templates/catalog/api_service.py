"""API service design and implementation team — Software Development."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="api_service",
    description="Designs, documents, and security-audits a production-ready API service with OpenAPI spec and implementation guide.",
    category="Software Development",
    tags=["api", "rest", "openapi", "backend", "security", "documentation"],
    agents=[
        AgentSpec(
            name="API Designer",
            role="RESTful API design and contract specialist",
            instructions=(
                "You are an API design expert with deep knowledge of REST principles, "
                "API versioning, and developer experience. For the given service, produce: "
                "complete OpenAPI 3.1 spec (YAML) including all endpoints, request/response schemas, "
                "authentication schemes, error codes, and examples. "
                "Apply REST best practices: resource naming, HTTP method semantics, status codes, "
                "HATEOAS links where appropriate, and pagination strategy. "
                "Include a changelog section and deprecation policy."
            ),
            config=AgentConfig(max_tokens=6000),
        ),
        AgentSpec(
            name="Backend Developer",
            role="API implementation and architecture specialist",
            instructions=(
                "You are a senior backend developer. Based on the API design, produce: "
                "recommended tech stack (language, framework, ORM) with justification, "
                "project structure (directory tree), "
                "middleware stack (auth, rate limiting, logging, CORS, validation), "
                "database schema aligned with the API resources, "
                "background job patterns for async operations, "
                "graceful shutdown and health check implementation, "
                "and a Docker + docker-compose setup for local development."
            ),
            config=AgentConfig(max_tokens=4000),
        ),
        AgentSpec(
            name="Security Auditor",
            role="API security review and hardening specialist",
            instructions=(
                "You are an API security specialist. Review the API design and produce: "
                "OWASP API Security Top 10 assessment (rate each risk as low/medium/high with mitigations), "
                "authentication and authorization audit (JWT validation, scope enforcement, token expiry), "
                "input validation vulnerabilities (injection, schema bypass), "
                "sensitive data exposure risks (PII in logs, overly verbose errors), "
                "rate limiting and DoS protection recommendations, "
                "security headers checklist, "
                "and a penetration testing checklist for the API."
            ),
            config=AgentConfig(max_tokens=3500),
        ),
        AgentSpec(
            name="Documentation Writer",
            role="Developer documentation and DX specialist",
            instructions=(
                "You are a technical documentation writer focused on developer experience. Produce: "
                "a Getting Started guide (under 5 minutes to first API call), "
                "authentication tutorial with code examples in Python, JavaScript, and cURL, "
                "3 common use case tutorials (step-by-step with sample code), "
                "error handling guide with all error codes explained, "
                "SDK usage guide (if SDKs are recommended), "
                "webhook integration guide, "
                "and a changelog template for future updates."
            ),
            config=AgentConfig(max_tokens=4000),
        ),
    ],
    debate_topics=[
        "What API style and authentication strategy best serves this service's consumers?",
        "REST with API key auth (simple, universally supported)",
        "REST with OAuth 2.0 (enterprise-grade, third-party integration ready)",
        "GraphQL (flexible queries, reduced over-fetching, single endpoint)",
        "gRPC (high performance, strong typing, ideal for internal microservices)",
    ],
    expected_outputs=[
        "Complete OpenAPI 3.1 specification (YAML)",
        "Tech stack and project structure recommendation",
        "Middleware and security configuration",
        "Database schema aligned with API resources",
        "OWASP API Security Top 10 assessment",
        "Getting Started guide with code examples",
        "3 use case tutorials",
        "Error code reference",
        "Penetration testing checklist",
    ],
))
