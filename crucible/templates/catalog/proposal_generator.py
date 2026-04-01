"""Sales proposal generation team — Sales."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="proposal_generator",
    description="Generates a compelling, customized sales proposal with business case, ROI analysis, and objection pre-handling.",
    category="Sales",
    tags=["sales", "proposal", "rfp", "b2b", "business case", "roi"],
    agents=[
        AgentSpec(
            name="Discovery Synthesizer",
            role="Customer needs and pain point synthesis specialist",
            instructions=(
                "You are a sales strategist. Synthesize the discovery call findings into: "
                "executive summary of the prospect's stated challenges and goals, "
                "unstated or implied needs (what they didn't say explicitly but is implied), "
                "decision criteria (how will they evaluate vendors?), "
                "political dynamics (who are the champions, skeptics, and blockers?), "
                "budget and timeline signals, "
                "and the single most compelling reason they should buy from you (not a list — one clear reason)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Proposal Writer",
            role="Sales proposal structure and persuasion specialist",
            instructions=(
                "You are a proposal writing expert. Write a complete proposal: "
                "cover page and executive summary (decision-ready, under 300 words), "
                "'Why Now' section (cost of inaction — what happens if they don't solve this?), "
                "solution section (tailored to their specific challenges, not a product brochure), "
                "implementation timeline and success plan, "
                "proof section (case study most similar to their situation, testimonials, data), "
                "pricing section (options: good / better / best with anchoring), "
                "and next steps / call to action."
            ),
            config=AgentConfig(max_tokens=4000),
        ),
        AgentSpec(
            name="ROI Calculator",
            role="Business case and financial justification specialist",
            instructions=(
                "You are a financial justification specialist. Build: "
                "ROI model with assumptions stated explicitly (conservative / likely / optimistic), "
                "payback period calculation, "
                "3-year NPV with discount rate assumption, "
                "cost of inaction quantification (what is the cost of staying with the status quo?), "
                "soft benefits that are harder to quantify but worth naming (risk reduction, morale, strategic optionality), "
                "and a one-page financial summary designed for the CFO's review."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Objection Handler",
            role="Pre-emptive objection and competitive positioning specialist",
            instructions=(
                "You are a competitive sales coach. Produce: "
                "anticipated objections based on the deal context (price, incumbent vendor, timing, risk), "
                "pre-emptive objection handling embedded in the proposal, "
                "competitive positioning section (why us over the 2-3 alternatives they're likely evaluating?), "
                "risk reversal mechanisms (pilot program, phased rollout, money-back guarantee options), "
                "and reference customer strategy (which references to offer for their specific concern)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
    ],
    debate_topics=[
        "What should lead the proposal to maximize the chance of a 'yes'?",
        "Lead with their pain (prove you listened, connect emotionally before rational case)",
        "Lead with the ROI (CFO-first, quantified value justifies approval)",
        "Lead with the solution (show you understand their technical needs)",
        "Lead with social proof (case study from similar company de-risks the decision)",
    ],
    expected_outputs=[
        "Executive summary (under 300 words)",
        "Complete proposal draft with all sections",
        "ROI model with 3-year NPV and payback period",
        "Good / better / best pricing structure",
        "Objection handling guide",
        "Competitive positioning section",
        "One-page financial summary for CFO",
    ],
))
