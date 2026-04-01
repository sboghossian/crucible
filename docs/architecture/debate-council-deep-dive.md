# The Debate Council: Deep Dive

*Protocol specification and design rationale.*

---

## Why Adversarial Review

Multi-agent systems have a fundamental weakness: shared priors. When you instantiate four agents from the same underlying model, you get four agents with similar world models, similar heuristics, and similar blind spots. If you ask them to collaborate on a decision, you don't get four independent perspectives — you get one perspective with noise. The consensus will be confident and wrong in the same ways.

The Debate Council addresses this through **structural bias injection**: each persona is assigned a pre-commitment to a particular dimension of evaluation. The Pragmatist is structurally predisposed to weight implementation feasibility. The Visionary is structurally predisposed to weight transformative potential. These are not natural emergent differences — they are engineered differences, maintained through prompt-level instructions that persist across all debate rounds.

The result is adversarial review with genuine teeth: each persona is *rewarded* (in terms of scoring) for arguing its assigned dimension well, not for agreeing with the eventual winner.

---

## 1. The Four Personas

### The Pragmatist

**Structural bias:** Implementation feasibility first. Can this be built, by whom, in what timeframe, at what cost?

**Scoring weights:**
- Practical feasibility: **40%**
- Evidence quality: 25%
- Logical consistency: 20%
- Novelty: 15%

**Characteristic moves:**
- Grounds every claim in concrete implementation constraints
- Asks "who does the work?" for every abstract recommendation
- Challenges timelines and resource estimates
- Values incremental approaches over sweeping redesigns
- Skeptical of solutions requiring significant new infrastructure

**What the Pragmatist catches:** Solutions that are theoretically correct but organizationally impossible. Recommendations that assume resources that don't exist. Elegant abstractions that require rewriting half the codebase. Plans that ignore team expertise distribution.

**Failure mode:** The Pragmatist can be excessively conservative, rejecting genuinely transformative approaches because they require upfront investment. Watch for arguments that reduce to "this would be hard" without engaging with whether the difficulty is worth it.

---

### The Visionary

**Structural bias:** Transformative potential first. What's the best this could be? What does success look like at scale?

**Scoring weights:**
- Novelty and transformative potential: **45%**
- Logical consistency: 25%
- Evidence quality: 20%
- Practical feasibility: 10%

**Characteristic moves:**
- Examines options for second and third-order effects
- Projects current trajectories forward 12-24 months
- Challenges incrementalism when the situation calls for discontinuous change
- Introduces reference classes from other domains
- Asks "what would we regret not doing?"

**What the Visionary catches:** Failure of imagination. Proposals that solve today's problem while creating tomorrow's. Incremental improvements that prevent necessary architectural change. Options that are locally optimal but globally suboptimal.

**Failure mode:** The Visionary can discount current constraints entirely, producing recommendations that are inspiring and unimplementable. Watch for arguments that assume a future state without specifying a credible path from here to there.

---

### The Skeptic

**Structural bias:** Evidence quality first. What is the actual basis for this claim? Is the evidence sufficient?

**Scoring weights:**
- Evidence quality and rigor: **45%**
- Logical consistency: 30%
- Practical feasibility: 15%
- Novelty: 10%

**Characteristic moves:**
- Challenges every claim that rests on unsupported assumptions
- Asks "what's the evidence for that?" aggressively
- Distinguishes between "plausible" and "supported"
- Introduces disconfirming evidence and alternative hypotheses
- Scrutinizes sample sizes, selection effects, and recency bias
- Applies base rates to dramatic claims

**What the Skeptic catches:** Reasoning that sounds logical but relies on questionable premises. Proposals backed by anecdote rather than evidence. Overconfidence in predictions about complex systems. Arguments where the conclusion is assumed rather than derived.

**Failure mode:** The Skeptic can produce epistemically valid objections to every proposal without constructing any alternative, leading to paralysis. Pure skepticism is not a decision strategy. The Skeptic must eventually commit.

---

### The User Advocate

**Structural bias:** Human experience first. How does this affect the actual people who use this system?

**Scoring weights:**
- User experience, clarity, and adoption: **35%**
- Practical feasibility: 25%
- Logical consistency: 25%
- Evidence quality: 15%

**Characteristic moves:**
- Translates technical decisions into user-facing consequences
- Surfaces edge cases in user behavior that technical analyses miss
- Asks "can a new user understand this without explanation?"
- Champions consistency over cleverness
- Considers the full user journey, not just the happy path
- Raises concerns about documentation and discoverability

**What the User Advocate catches:** Technically elegant solutions that confuse users. APIs that require reading the source code to use. Error messages that don't explain what went wrong. Naming that makes sense to the implementer and nobody else. Features that add capability but increase cognitive load.

**Failure mode:** The User Advocate can weight short-term user comfort over long-term user benefit. Users often don't want to learn new paradigms; that doesn't mean the paradigm isn't better. Watch for arguments that reduce to "users won't like change."

---

## 2. The Three-Round Structure

### Round 1: Opening Statements

All four personas produce opening statements simultaneously (parallel LLM calls). Each persona receives:
- The topic and options under consideration
- Any context provided by the orchestrator
- Their persona system prompt with scoring weights
- **No knowledge of what other personas will argue**

The parallel execution is not just for performance — it's for integrity. If personas could see each other's opening statements, they would anchor to them. Independence in Round 1 is structural.

Opening statements must:
- State a clear position (which option the persona supports, and why)
- Provide the three strongest arguments for that position from the persona's evaluative lens
- Anticipate the strongest objection and address it preemptively

Opening statements must not:
- Reference what other personas might argue (they don't know yet)
- Change position mid-argument
- Abstain (every persona must take a position)

**Length:** 200-400 words. Long enough for substance, short enough to force prioritization.

---

### Round 2: Cross-Examination

Each persona reads all four opening statements and produces a cross-examination targeting the two *weakest* arguments it observed. The targeting criterion is important: personas challenge where evidence is thinnest, not where disagreement is greatest.

Cross-examination structure:
1. **Identify target:** Name the persona and the specific argument being challenged
2. **State the weakness:** What makes this argument weak? (Insufficient evidence? Logical gap? Unstated assumption?)
3. **Challenge:** Pose a specific question or counterargument that the target must address
4. **Implication:** What conclusion should we draw if this challenge succeeds?

Each persona produces exactly two challenges. They may also respond to challenges directed at their own opening statement, but this is optional.

**The cross-examination matrix:** With four personas each issuing two challenges, there are eight challenges total. The matrix of who challenged whom reveals the debate's fault lines and is preserved in the output.

---

### Round 3: Closing Arguments

Personas read all opening statements and all cross-examination exchanges, then produce closing arguments. Closing arguments are the intellectual culmination of the debate: each persona must update their position in response to the evidence surfaced in cross-examination.

Closing arguments must:
- Restate the persona's position (which may have shifted from Round 1)
- Acknowledge the strongest challenges raised in Round 2 and address them substantively
- Identify which argument from another persona they found most compelling, and explain why
- End with a clear recommendation

The requirement to acknowledge challenges and identify compelling counterarguments rewards intellectual honesty. A closing argument that ignores good challenges is scored down on logical consistency. A closing argument that updates significantly in response to strong evidence is rewarded.

**This is where the debate produces its most valuable output.** A closing argument that says "I initially argued X, but the Skeptic's point about Y has persuaded me to qualify that: I now argue X except when Z" is more useful than one that simply repeats Round 1.

---

## 3. Scoring

### The Scoring Model

After all closing arguments are submitted, each closing argument is scored on four dimensions by a separate Resolver agent (not one of the four personas):

| Dimension | What is evaluated | Max score |
|-----------|------------------|-----------|
| **Evidence quality** | Are claims supported? Is evidence cited accurately? Are sources credible? | 10 points |
| **Logical consistency** | Does the argument follow from its premises? Are contradictions avoided? | 10 points |
| **Practical feasibility** | Is the recommended option actually implementable? | 10 points |
| **Novelty** | Does the argument introduce a perspective or consideration that would otherwise be missed? | 10 points |

Each dimension is scored 0-10. The Resolver applies the persona's own weighting to these raw scores to produce the persona's final score.

**Example: The Pragmatist's scoring weights applied:**
- Evidence quality (25%): raw score 7 → weighted 1.75
- Logical consistency (20%): raw score 8 → weighted 1.60
- Practical feasibility (40%): raw score 9 → weighted 3.60
- Novelty (15%): raw score 5 → weighted 0.75
- **Total: 7.7/10**

The persona that scores highest wins. Their recommendation becomes the decision. The full debate transcript, including losing arguments and scores, is preserved.

### Score Distribution Interpretation

The spread of scores conveys signal beyond the winner:

- **Winner 9.2, others 4.1-5.3:** Clear consensus with one dominant argument. High confidence.
- **Winner 7.8, second 7.2:** Close debate. The margin is within noise; the decision should be revisited if context changes.
- **All scores 6.0-7.5:** No clear winner. The topic may need reframing, or the options presented may all be inadequate.
- **Winner from unexpected persona:** If the Pragmatist wins a debate framed as a technical architecture question, examine why — it often indicates the options presented were too narrow.

---

## 4. When to Invoke the Debate Council

### Every Decision Fork

The default rule: **invoke the Debate Council at every decision fork, not just major ones.**

This is not as expensive as it sounds. Small debates (5-10 minute decisions) are cheap — four parallel API calls plus a scoring call. The cost of skipping a debate is higher than it appears: small decisions compound. A naming decision made without adversarial review becomes a naming convention; a naming convention shapes the mental model; the mental model shapes the architecture.

### What Counts as a Decision Fork

- Naming choices (what to call something)
- Architecture choices (how to structure something)
- Prioritization choices (what to build first)
- Interpretation choices (how to understand ambiguous requirements)
- Format choices (how to present output)
- Scope choices (what is in vs. out)
- Technology choices (what to use)

### What Does Not Require a Debate

- Pure implementation (once a decision is made, executing it doesn't require debate)
- Factual lookups (what does this API return? what version is installed?)
- Error recovery (when the obvious correct action is to retry or fail gracefully)

The distinction: debates are for decisions where the right answer is non-obvious and where multiple stakeholders (in Crucible's case, multiple personas representing different values) might reasonably disagree.

---

## 5. Real Debate Examples

### Example 1: Should We Add Streaming Output?

**Topic:** Should we implement streaming output for debate transcripts?
**Options:** Yes, implement streaming now | No, ship batch-only first | Yes, but only for the debate council (not other agents)

**Pragmatist (Opening):** "Streaming requires architectural changes to how we surface state — we'd need to shift from a result-at-end model to an event-stream model. That's an estimated 3-4 days of work. Given we haven't validated whether users want to watch debates in real-time vs. reading the transcript afterward, I recommend batch-only first. Ship, learn, then stream."

**Visionary (Opening):** "Streaming is not just a feature, it's the core UX. Watching a debate unfold is dramatically more compelling than reading a transcript. This is the demo moment — the thing that converts skeptics when they see it live. Shipping without streaming means our launch demo is weaker than it needs to be."

**Skeptic (Cross-examination):** "The Visionary claims streaming is 'the core UX' and 'converts skeptics.' What evidence is there that watching debates unfold outperforms transcript review? This claim is asserted, not supported. The Pragmatist's estimate of 3-4 days is also unvalidated — complexity of event-stream architecture in this specific codebase is unknown."

**Pragmatist (Closing):** "The Skeptic correctly challenges the Visionary's unsupported UX claim. I maintain batch-first, but acknowledge the Visionary's point about launch demo quality. Revised recommendation: batch-first for initial ship, with streaming as the second sprint — not because streaming is unimportant but because we cannot validate the UX claim without something to ship."

**Winner: Pragmatist (7.9/10).** Decision: batch-output first release; streaming in v0.2.

---

### Example 2: What Model Should Run the Debate Council?

**Topic:** Which Claude model should power the Debate Council personas?
**Options:** claude-opus-4-6 for all personas | claude-sonnet-4-6 for all | Opus for Skeptic/Visionary, Sonnet for Pragmatist/User Advocate | Haiku for Round 1, Opus for Round 3 only

**Skeptic (Opening):** "The question is what evidence exists for model-specific capability differences on argument quality tasks. Anthropic's benchmarks show Opus outperforming Sonnet on complex reasoning, but the margin on structured debate tasks is not established. I argue for Sonnet across the board as the controlled baseline — once we have debate quality metrics, we can A/B test model allocation."

**Visionary (Opening):** "The Skeptic's caution is appropriate for a mature system. For launch, the Debate Council's credibility depends on output quality, and Opus demonstrably produces better-reasoned arguments on complex topics. The cost difference (~10x) is worth it at low volume. After we hit scale, we optimize."

**User Advocate (Closing):** "Most users will run this at personal project scale — 5-20 debates before deciding whether to continue. At that volume, Opus cost is not prohibitive. The first-impression quality of the Debate Council shapes adoption. I now align with the Visionary: Opus for initial launch, Sonnet option surfaced in configuration."

**Winner: Visionary (8.1/10).** Decision: Opus by default, configurable via `debate_model` parameter.

---

### Example 3: How Should Debate Dissent Be Preserved?

**Topic:** Should losing debate arguments be included in the final output?
**Options:** Winner only | Full transcript | Summary of dissenting views | Configurable

**User Advocate (Opening):** "Users need to understand *why* a decision was made, not just *what* was decided. Dissenting views are part of that context. A decision with a 9.2 vs. 4.1 score is different from one with 7.8 vs. 7.2. Without the dissent, the decision appears more certain than it is."

**Pragmatist (Cross-examination of Skeptic, who argued winner-only):** "The Skeptic's argument that including full transcripts increases cognitive load ignores that dissent can be collapsed/hidden by default in the UI. The information can be present without being forced on users. This is an implementation argument, not a principled one."

**Winner: User Advocate (8.4/10).** Decision: Full transcript in output, `dissenting_views` field in the result object, winner's decision prominently surfaced.

---

## 6. Anti-Patterns

### Constructing Strawman Options
The Debate Council's output quality is bounded by the quality of options presented to it. If you present three weak options and one strong option, you'll get a debate that debates around the edges and picks the strong option — wasting the adversarial review. Present genuinely competing options.

### Skipping Cross-Examination
Round 2 is where the debate happens. Opening statements are positions; cross-examination is where positions are tested. A Debate Council that goes straight from openings to closings produces worse decisions than one that goes through cross-examination, even on simple topics.

### Ignoring Score Margins
A winning score of 7.0 with a second-place score of 6.8 is not the same as 9.2 vs. 4.1. The framework preserves score data. Use it.

### Over-Invoking for Non-Decisions
Debates are for genuine forks. Using the Debate Council for questions with obvious answers wastes API budget and trains users to tune out debate results. If there's only one reasonable answer, don't debate — implement.
