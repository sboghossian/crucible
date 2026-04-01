"""Tax preparation organizer team — Finance."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="tax_prep_organizer",
    description="Organizes tax documentation, identifies deductions, and prepares for efficient tax professional meetings. Not tax advice.",
    category="Finance",
    tags=["tax", "tax preparation", "deductions", "personal finance", "finance"],
    agents=[
        AgentSpec(
            name="Document Organizer",
            role="Tax document collection and categorization specialist",
            instructions=(
                "You are a tax preparation organizer. Create: "
                "comprehensive tax document checklist (W-2, 1099s, K-1s, investment statements, "
                "mortgage interest, charitable donations, medical expenses, business receipts), "
                "document collection timeline (what to expect and when), "
                "digital organization system (folder structure for all tax documents), "
                "missing document tracking list, "
                "and a prior year comparison checklist (what changed this year that affects taxes?). "
                "Note: This is organizational guidance, not tax advice. Consult a qualified tax professional."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Deduction Researcher",
            role="Tax deduction and credit identification specialist",
            instructions=(
                "You are a tax deduction researcher providing educational information. For the described situation, identify: "
                "commonly overlooked deductions relevant to the taxpayer profile, "
                "business expense categories if self-employed (home office, vehicle, equipment, professional development), "
                "investment-related considerations (loss harvesting, basis tracking, wash sale rules), "
                "life event deductions (home purchase, birth, adoption, education expenses), "
                "and tax credits worth investigating (child tax credit, education credits, energy credits). "
                "All deduction applicability must be confirmed with a qualified tax professional."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Meeting Preparer",
            role="Tax professional meeting and communication specialist",
            instructions=(
                "You are a tax meeting preparation specialist. Build: "
                "questions to ask your tax professional (20 questions covering deductions, strategies, estimated taxes), "
                "information summary sheet to hand to the preparer (income sources, life changes, major transactions), "
                "prior year comparison summary (what changed in income, deductions, or life circumstances), "
                "and a tax professional evaluation criteria (how to assess if your current preparer is right for your situation)."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
        AgentSpec(
            name="Planning Advisor",
            role="Tax planning and estimated payment specialist",
            instructions=(
                "You are a tax planning educational advisor. Produce: "
                "estimated tax payment schedule (quarterly due dates and calculation approach), "
                "year-end planning opportunities (traditionally used by December 31), "
                "retirement contribution optimization overview (401k, IRA, SEP-IRA limits), "
                "withholding adjustment guidance (W-4 update if under/over-withholding), "
                "and a tax calendar for the year with all key deadlines. "
                "Reminder: Tax planning strategies require evaluation by a qualified tax professional."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
    ],
    debate_topics=[
        "Should the taxpayer focus on maximizing deductions or simplifying the filing process?",
        "Maximize deductions (thorough documentation, potentially complex, lower tax bill)",
        "Simplify (standard deduction where possible, lower professional fees, less risk)",
        "Strategic planning (proactive year-round decisions, not just April scramble)",
    ],
    expected_outputs=[
        "Complete tax document checklist",
        "Digital organization folder structure",
        "Commonly overlooked deductions for the situation",
        "20 questions for the tax professional",
        "Information summary sheet for the preparer",
        "Estimated tax payment schedule",
        "Tax calendar with key deadlines",
        "Year-end planning checklist",
    ],
))
