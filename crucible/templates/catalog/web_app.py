"""Web application scaffolding team — Software Development."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="web_app",
    description="Designs and scaffolds a full-stack web application with architecture decisions, tech stack selection, and CI/CD setup.",
    category="Software Development",
    tags=["web", "fullstack", "architecture", "react", "nextjs", "devops", "scaffold"],
    agents=[
        AgentSpec(
            name="Architect",
            role="System architect and tech stack decision maker",
            instructions=(
                "You are a senior software architect specializing in web applications. "
                "Given the application description, produce: a system architecture diagram (Mermaid), "
                "tech stack recommendation with justification (frontend framework, backend, database, cache, "
                "auth, file storage, deployment platform), scalability considerations (expected load), "
                "third-party integrations needed, security architecture (auth flow, RBAC, data encryption), "
                "and a risk register with mitigation strategies. Justify every major decision."
            ),
            config=AgentConfig(max_tokens=4000),
        ),
        AgentSpec(
            name="Frontend Developer",
            role="Frontend architecture and component design specialist",
            instructions=(
                "You are a senior frontend developer. Based on the architecture, produce: "
                "project structure (directory tree), core page/route inventory, "
                "component hierarchy for 3 key screens, state management strategy, "
                "API integration patterns (React Query / SWR / or server components), "
                "design system recommendations (shadcn/ui, Radix, custom), "
                "performance strategy (lazy loading, code splitting, SSR vs CSR vs ISR), "
                "and a package.json with all dependencies pinned to latest stable versions."
            ),
            config=AgentConfig(max_tokens=4000),
        ),
        AgentSpec(
            name="Backend Developer",
            role="API and database design specialist",
            instructions=(
                "You are a senior backend developer. Produce: "
                "RESTful or GraphQL API design for the core domain (endpoints, methods, request/response shapes), "
                "database schema (tables/collections, indexes, relationships), "
                "authentication and session management implementation plan, "
                "background job architecture (queues, workers), "
                "caching strategy (what to cache, TTLs), "
                "error handling and logging strategy, "
                "and rate limiting / API security hardening checklist."
            ),
            config=AgentConfig(max_tokens=4000),
        ),
        AgentSpec(
            name="DevOps Engineer",
            role="Infrastructure, CI/CD, and deployment specialist",
            instructions=(
                "You are a senior DevOps engineer. Produce: "
                "a complete GitHub Actions CI/CD pipeline (YAML) with lint, test, build, and deploy stages, "
                "Docker and docker-compose configuration for local development, "
                "production deployment architecture (cloud provider recommendation, containers vs PaaS), "
                "environment variables management strategy, "
                "database migration workflow, "
                "monitoring and alerting setup (which tools, what to alert on), "
                "and a production readiness checklist."
            ),
            config=AgentConfig(max_tokens=4000),
        ),
        AgentSpec(
            name="QA Engineer",
            role="Testing strategy and quality assurance specialist",
            instructions=(
                "You are a senior QA engineer. Produce: "
                "a testing pyramid strategy (unit, integration, e2e ratios), "
                "test file structure and naming conventions, "
                "critical path test cases for the 5 most important user journeys, "
                "API contract testing approach, "
                "performance testing plan (k6 or Artillery scenarios), "
                "accessibility testing checklist (WCAG 2.1 AA), "
                "and a bug triage and severity classification guide."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
    ],
    debate_topics=[
        "Which tech stack best serves this application's requirements and team?",
        "Next.js full-stack (unified codebase, Vercel deployment)",
        "React + separate Node/FastAPI backend (clear separation of concerns)",
        "Remix (progressive enhancement, nested routing, built-in data loading)",
        "SvelteKit (performance-first, smaller bundle, simpler mental model)",
    ],
    expected_outputs=[
        "System architecture diagram (Mermaid)",
        "Tech stack decision document with justifications",
        "Directory structure and project scaffold",
        "Database schema and API endpoint inventory",
        "GitHub Actions CI/CD pipeline YAML",
        "Docker and docker-compose configuration",
        "Testing strategy and critical path test cases",
        "Production readiness checklist",
        "Risk register with mitigations",
    ],
))
