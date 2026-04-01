# Module 7: Predictive Analysis

---

## Learning Objectives

By the end of this module, you will be able to:
1. Apply structured scenario analysis to technology decisions with quantified probabilities
2. Identify the skills that become more and less valuable under different scenarios
3. Use the Crucible Forecaster agent to generate probabilistic predictions with reference classes
4. Distinguish between leading indicators and lagging indicators of AI capability progress

---

## 7.1 Why Scenario Analysis

Single-point predictions about technology are almost always wrong. The question isn't "what will happen?" — it's "what are the plausible paths, and how should I prepare for each?"

Scenario analysis acknowledges that the future is uncertain while still enabling reasoned action. The discipline is: identify 2-4 structurally different scenarios, assign probabilities based on current evidence, identify the leading indicators that would shift probability between scenarios, and build strategies that are robust across the most likely scenarios.

The three scenarios in Crucible's forecast (Module 1 research document) are:
- **Accelerated Augmentation (30%):** Capability improvements continue; productivity paradox resolves; developer output 2-5x
- **Managed Transition (55%):** Decelerating capability; partial productivity gains; significant skills bifurcation
- **Turbulent Reckoning (15%):** High-profile failure triggers regulatory response; enterprise adoption freezes

Notice that 30% probability scenarios are not "unlikely" — they're "less likely than the base case." A 30% probability event happens roughly 1 in 3 times. Planning only for the base case means you're unprepared one time in three.

---

## 7.2 Leading Indicators

The scenarios are not fixed — they shift as evidence arrives. These are the leading indicators that would shift probabilities:

**Indicators that shift toward Accelerated Augmentation:**
- SWE-bench Pro scores consistently exceed 50% for top systems
- METR-style productivity studies show improving outcomes year-over-year
- Enterprise AI coding tool adoption rate exceeds 50% within 18 months
- A major software product (widely used, not a toy) is shipped primarily by AI agents

**Indicators that shift toward Turbulent Reckoning:**
- A high-profile security incident with attributable root cause in AI-generated code
- Regulatory action (EU AI Act enforcement action, US CISA guidance) that creates liability for AI code
- Legal judgment establishing developer liability for AI-generated code defects
- METR-style study shows no productivity improvement even for experienced developers

**Indicators that shift toward Managed Transition (staying in the base case):**
- Productivity improvements, but slower than forecast (1.2-1.5x, not 3x)
- Enterprise adoption with governance requirements — slower but less risky
- Skill bifurcation becoming visible in salary data (AI-fluent developers earning significant premium)

---

## 7.3 Skills Under Each Scenario

### Accelerated Augmentation

If developer output genuinely scales 2-5x, the bottleneck shifts from writing code to:
- **Specifying what to build:** Precise requirements, testable acceptance criteria
- **Evaluating what was built:** Does this do what we intended? Is it correct?
- **System architecture:** AI handles components; humans design how components relate
- **Judgment at the frontier:** Novel problems AI hasn't seen in training

Devalued in this scenario:
- Routine implementation
- Code reading (AI summarizes)
- Repetitive debugging (AI diagnoses common patterns)

### Managed Transition (base case)

The skills bifurcation is the dominant story:
- **AI workflow design:** Structuring tasks to minimize the Devin Gap
- **Output verification:** Knowing what to check and how deeply
- **Domain expertise:** The value of knowing your domain deeply *increases* because you can evaluate AI output in that domain
- **Cross-functional collaboration:** As technical barriers lower, the differentiator is working with non-technical stakeholders

Devalued:
- Pure syntax knowledge
- Boilerplate and standard pattern implementation
- Standard algorithm implementation from scratch

### Turbulent Reckoning

If there's regulatory response:
- **AI audit and compliance:** Understanding what AI did and documenting it
- **Traditional software engineering fundamentals:** Ironic, but teams that maintained fundamentals are better positioned
- **Security engineering:** AI-specific vulnerability patterns become a specialized skill
- **Risk management:** Assessing and documenting AI risk in production systems

---

## 7.4 The Crucible Forecaster

The Forecaster agent produces structured probabilistic output:

```python
import asyncio
from crucible import Orchestrator

async def forecast():
    orch = Orchestrator()

    result = await orch.standalone_forecast(
        topic="Adoption rate of AI coding agents in enterprise software teams",
        timeframe="2027",
        context="""
        Current state: 73% individual dev daily usage (Stack Overflow 2026).
        Enterprise adoption: significant but slower than individual.
        Key blocker: security and IP concerns, integration costs.
        Base rate: previous dev tool transitions (Docker: 4yr to 50% enterprise).
        """
    )

    for scenario in result.scenarios:
        print(f"\n{scenario.name} ({scenario.probability:.0%})")
        print(f"  {scenario.summary}")
        print(f"  Key assumption: {scenario.key_assumption}")
        print(f"  Would be wrong if: {scenario.disconfirming_condition}")

asyncio.run(forecast())
```

The Forecaster output includes:
- Scenarios with probabilities
- Reference classes (what analogous historical situations look like)
- Disconfirming conditions for each scenario (what would falsify this prediction)
- Leading indicators to monitor

---

## 7.5 Calibration

A prediction is only as good as its calibration — the alignment between stated probability and actual frequency. A forecaster who says "80% likely" should be right 80% of the time.

The Forecaster agent is not calibrated in the statistical sense — we don't have enough evaluation data yet. But you can apply calibration disciplines to its output:

**Reference class forecasting:** Anchor predictions to base rates from analogous situations. How long did previous technology transitions take? What fraction of predicted transitions happened on schedule?

**Debiasing:** Technology predictions skew optimistic (we consistently underestimate time to adoption) and often miss the dominant failure mode. Consciously look for the pessimistic reference class.

**Prediction tracking:** Log the Forecaster's predictions and check them as time passes. This builds institutional calibration data and reveals systematic biases.

---

## 7.6 Applying Scenario Analysis to Your Own Career

The skill scenarios above are population-level predictions. Your personal situation may differ. Apply the framework:

1. **Map your current skills** against the three scenarios. Where are you well-positioned? Where are you exposed?

2. **Identify your high-leverage skill investments.** Which skills are valuable across all three scenarios? (Cross-scenario robustness is the goal — hedge against scenario uncertainty.)

3. **Identify your early warning indicators.** What events would tell you that one scenario is materializing? What would you do differently if that happened?

4. **Distinguish between durable skills and timely ones.** Domain expertise, system thinking, and judgment are durable. Specific tool knowledge is timely. Invest asymmetrically.

---

## Key Concepts

- **Scenario analysis:** 2-4 structurally different futures with quantified probabilities
- **Leading indicators:** Events that shift scenario probabilities — monitor these
- **Skills under scenarios:** What becomes more/less valuable changes by scenario
- **Forecaster agent:** Generates probabilistic predictions with reference classes and disconfirming conditions
- **Calibration disciplines:** Reference class forecasting, debiasing, prediction tracking

---

## Hands-On Exercise

**Exercise 7.1: Build your personal skills scenario matrix**

Create a 3×3 matrix: your top 5 current skills × the 3 scenarios. For each cell, assess: Does this skill become more valuable, less valuable, or unchanged?

What does this tell you about your career strategy?

**Exercise 7.2: Run a forecast with Crucible**

Pick a prediction relevant to your work (adoption of a technology, shift in a market, capability of a tool) and run it through the Crucible Forecaster. Compare the output to your prior intuition. What did it surface that you hadn't considered?

**Exercise 7.3: Design a leading indicator dashboard**

For the Managed Transition scenario (base case), identify 5 leading indicators you could monitor monthly. What data sources would you use? What would the dashboard look like?

---

## Discussion Questions

1. The base case scenario (55% probability) includes "significant skills bifurcation." What does it mean to be on the right side of a skills bifurcation? What does it mean to be on the wrong side?

2. Gartner projects 80% of engineers need upskilling by 2027. What does "upskilling" mean in this context? Is it primarily technical, or primarily meta-cognitive?

3. The Turbulent Reckoning scenario (15%) is assigned low probability. But 15% is not negligible — it happens roughly 1 in 7 times. How should you weight a 15% scenario in decision-making?

4. "Durable skills vs. timely skills" — what examples from your own field would you add to the list? What skill did you invest in that became timely (and now devalued)?

---

## References

- Forecast document: [docs/research/forecast-2027.md](../docs/research/forecast-2027.md)
- Gartner Technology and Skills Forecast 2025
- METR productivity study, 2026
- Philip Tetlock, *Superforecasting* (reference for calibration methodology)
- Stack Overflow Developer Survey 2026
