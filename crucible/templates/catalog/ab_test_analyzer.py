"""A/B test design and analysis team — Data Science."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="ab_test_analyzer",
    description="Designs, analyzes, and interprets A/B tests with statistical rigor, including power analysis and decision framework.",
    category="Data Science",
    tags=["a/b testing", "experimentation", "statistics", "conversion rate", "hypothesis testing"],
    agents=[
        AgentSpec(
            name="Experiment Designer",
            role="Hypothesis formulation and test design specialist",
            instructions=(
                "You are an experimentation specialist. Design the A/B test: "
                "null and alternative hypothesis statements, "
                "primary and secondary metrics (guard rail metrics to monitor for regressions), "
                "minimum detectable effect (MDE) definition (what change is business-meaningful?), "
                "statistical power analysis (sample size required at α=0.05, power=0.80), "
                "randomization unit (user-level, session-level, page-level — and why), "
                "experiment duration (accounting for novelty effect and weekly seasonality), "
                "and holdout group strategy if appropriate."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Statistician",
            role="Statistical analysis and significance testing specialist",
            instructions=(
                "You are a statistician specializing in online experiments. Produce: "
                "appropriate test selection (t-test, Mann-Whitney, chi-squared, z-test for proportions — with justification), "
                "p-value and confidence interval interpretation guide, "
                "multiple comparisons correction (Bonferroni, Benjamini-Hochberg), "
                "segmented analysis approach (which segments to analyze and why), "
                "variance reduction techniques (CUPED, stratification), "
                "and common statistical mistakes to avoid (peeking, stopping early, p-hacking)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Threat Assessor",
            role="Experiment validity and bias specialist",
            instructions=(
                "You are an experiment validity specialist. Check for: "
                "sample ratio mismatch (SRM) — is traffic split as expected?, "
                "novelty effect risk (is the effect driven by newness, not true value?), "
                "selection bias in randomization, "
                "network effects / SUTVA violations (users influencing each other), "
                "instrumentation bias (is the metric being measured correctly?), "
                "and Simpson's paradox risk (does the aggregate result hide segment-level reversals?)."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
        AgentSpec(
            name="Decision Advisor",
            role="Ship / no ship decision framework specialist",
            instructions=(
                "You are an experiment decision strategist. Build: "
                "ship / no-ship / iterate decision framework with explicit criteria, "
                "trade-off analysis (wins on primary metric vs. losses on guard rails), "
                "long-term vs. short-term effect reasoning (does this degrade over time?), "
                "rollout strategy recommendation (0% → 10% → 50% → 100%), "
                "winner and loser analysis (what can we learn from why this variant won or lost?), "
                "and next experiment recommendation based on this result."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
    ],
    debate_topics=[
        "Should we ship this variant based on the experimental results?",
        "Ship: statistically significant improvement on primary metric justifies rollout",
        "Do not ship: guard rail metric regression or effect too small to matter",
        "Iterate: promising signal but insufficient effect size or validity concerns",
        "Run longer: underpowered, need more data before deciding",
    ],
    expected_outputs=[
        "Null/alternative hypothesis statements",
        "Sample size calculation with power analysis",
        "Experiment duration and randomization design",
        "Statistical test selection with justification",
        "Experiment validity threat assessment",
        "Ship/no-ship decision framework",
        "Rollout strategy",
        "Next experiment recommendation",
    ],
))
