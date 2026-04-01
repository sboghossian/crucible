"""Terms of Service and Privacy Policy generation team — Legal."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="terms_of_service_generator",
    description="Generates Terms of Service, Privacy Policy, and Cookie Policy for a digital product with jurisdiction-appropriate clauses.",
    category="Legal",
    tags=["terms of service", "privacy policy", "legal", "saas", "ecommerce", "compliance"],
    agents=[
        AgentSpec(
            name="Terms Drafter",
            role="Terms of Service structure and clause specialist",
            instructions=(
                "You are a legal document drafter. Write a Terms of Service covering: "
                "acceptance of terms mechanism, "
                "description of services and eligibility, "
                "user account registration and responsibilities, "
                "acceptable use policy (what users may and may not do), "
                "intellectual property ownership (who owns user content? what license does the platform get?), "
                "payment terms and refund policy (if applicable), "
                "service modifications and termination rights (yours and theirs), "
                "disclaimer of warranties and limitation of liability, "
                "dispute resolution and governing law (arbitration clause?), "
                "and changes to terms notification process. "
                "Note: This is a template requiring review by qualified legal counsel before use."
            ),
            config=AgentConfig(max_tokens=5000),
        ),
        AgentSpec(
            name="Privacy Policy Writer",
            role="Privacy policy drafting and GDPR/CCPA compliance specialist",
            instructions=(
                "You are a privacy policy specialist. Draft a comprehensive privacy policy: "
                "what personal data is collected (account, usage, device, payment, communications), "
                "how data is collected (directly, automatically, from third parties), "
                "purposes of processing and legal basis, "
                "data sharing with third parties (categories of recipients), "
                "data retention periods, "
                "data subject rights section (access, correction, deletion, portability, opt-out), "
                "security measures overview, "
                "children's privacy statement, "
                "international transfer disclosures (SCCs, adequacy decisions), "
                "and contact information for privacy inquiries."
            ),
            config=AgentConfig(max_tokens=4000),
        ),
        AgentSpec(
            name="Cookie Policy Author",
            role="Cookie compliance and consent mechanism specialist",
            instructions=(
                "You are a cookie compliance specialist. Produce: "
                "cookie policy explaining categories (essential, analytics, marketing, preferences), "
                "specific cookies used with purpose and duration, "
                "consent management platform (CMP) recommendation, "
                "cookie banner implementation guide (pre-consent vs. opt-in requirements by jurisdiction), "
                "opt-out instructions for each cookie category, "
                "and third-party cookie inventory (analytics, advertising, social media pixels)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Compliance Reviewer",
            role="Cross-jurisdiction compliance and risk reviewer",
            instructions=(
                "You are a legal compliance reviewer. Assess the documents for: "
                "GDPR compliance (EU users: lawful basis, rights, DPO requirement), "
                "CCPA/CPRA compliance (California users: right to know, delete, opt-out of sale), "
                "CAN-SPAM and CASL compliance (email marketing), "
                "COPPA compliance (if service is available to under-13s in the US), "
                "jurisdiction-specific requirements checklist, "
                "and high-risk clauses flagged for attorney review (arbitration, class action waiver, IP assignment)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
    ],
    debate_topics=[
        "How should the dispute resolution clause be structured?",
        "Mandatory arbitration with class action waiver (protects company, controversial)",
        "Court jurisdiction with venue selection (more user-friendly, higher litigation exposure)",
        "Optional mediation first, then arbitration (balanced, good faith signal)",
    ],
    expected_outputs=[
        "Complete Terms of Service draft",
        "Complete Privacy Policy draft",
        "Cookie Policy with category breakdown",
        "Cookie banner implementation guide",
        "Cross-jurisdiction compliance checklist",
        "High-risk clauses flagged for attorney review",
    ],
))
