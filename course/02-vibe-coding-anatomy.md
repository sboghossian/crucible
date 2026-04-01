# Module 2: Anatomy of Vibe Coding

---

## Learning Objectives

By the end of this module, you will be able to:
1. Define vibe coding with precision — what it is, what it isn't, and who coined it
2. Distinguish between the three variants of vibe coding and their different risk profiles
3. Identify the conditions under which vibe coding produces good vs. bad outcomes
4. Apply a framework for deciding when to vibe-code and when to write

---

## 2.1 Origin and Definition

On **February 2, 2025**, Andrej Karpathy posted on X:

> "There's a new kind of coding I call 'vibe coding', where you fully give in to the vibes, embrace exponentials, and forget that the code even exists. [...] I'm building a project or webapp, but it's not really coding — I just see stuff, say stuff, run stuff, and copy paste stuff, and it mostly works."

The post was not describing a new technique — it was naming a behavior already widespread. The naming did something: it crystallized the phenomenon, gave critics and advocates a shared reference point, and enabled the cultural conversation that followed.

Collins Dictionary named *vibe coding* its Word of the Year for 2025 — a notable choice for a technical term, and evidence that the practice had escaped developer circles and entered mainstream discourse.

**Precise definition:** Vibe coding is the practice of creating software by describing desired outcomes to an AI assistant and iterating on its output without necessarily writing or understanding the underlying code.

The qualifying phrase "without necessarily" is important. Vibe coding exists on a spectrum, from "I have no idea what's in this file" to "I'm using AI for the mechanical parts but I understand the output." The public debate conflates these cases; this module distinguishes them.

---

## 2.2 The Three Variants

### Variant 1: Novice Vibe Coding

The user has no model of the underlying code. They describe what they want, accept or reject AI output based on whether it appears to work, and iterate. The code is a black box.

**Who does this:** Non-developers building personal tools. Business people prototyping ideas. Students learning by doing (questionable effectiveness).

**What it produces:** Working prototypes, quickly. Non-developers can now build functional web apps, data pipelines, and automation scripts without programming background.

**Where it breaks down:**
- Maintenance: when something breaks, the user cannot diagnose it without AI help, and AI may not be able to diagnose it without more context than the user can provide
- Security: novice vibe coders routinely ship credential-handling, authentication, and data storage code they haven't read and don't understand
- Scale: code that works for 10 users may fail for 1000 in non-obvious ways that only a developer with production experience would anticipate

**Risk profile:** High for any code touching user data, financial transactions, or production systems. Low for personal automation, throwaway prototypes, and experiments.

---

### Variant 2: Expert Vibe Coding

The user has deep programming experience. They use AI for boilerplate, implementation detail, and code they understand architecturally but don't want to write mechanically. They review AI output, understand what it does, and modify as needed.

**Who does this:** Senior developers who have learned to delegate mechanical implementation while retaining design control. This is Karpathy's actual practice — he is not a novice.

**What it produces:** Faster implementation of well-understood tasks. The expert knows what correct code looks like and can verify AI output quickly.

**Where it breaks down:**
- Verification overhead eats speed gains on unfamiliar code
- Expert knowledge can create overconfidence — the code looks right because the expert knows the domain, but AI may have introduced subtle bugs
- Works well in familiar domains, poorly in new ones

**Risk profile:** Moderate. Substantially lower than novice vibe coding because the developer can evaluate output quality. The main risk is speed-induced complacency on verification.

---

### Variant 3: Collaborative Vibe Coding

A team where AI-fluent members use AI to produce code that AI-unfluent members review, direct, and integrate. The AI is the implementation layer; humans retain architecture and review.

**Who does this:** Cross-functional teams where some members are developers and others are domain experts (data scientists, analysts, researchers).

**What it produces:** Higher throughput on well-defined tasks with domain-expert oversight.

**Where it breaks down:**
- The non-developer reviewer may not catch implementation bugs even while catching domain errors
- Knowledge transfer is asymmetric: if the only AI-fluent developer leaves, the team loses most of its coding capacity
- Team dynamics can be strained when AI generates code faster than humans can review it

**Risk profile:** Depends on review quality. If human reviewers understand what they're reviewing, moderate. If they don't, high.

---

## 2.3 The Vibe Coding Performance Envelope

Vibe coding performs well within a specific envelope. Outside that envelope, it degrades.

**High performance conditions:**
- Well-defined tasks with clear acceptance criteria
- Greenfield work with no complex system interactions
- Domains the AI model has seen extensively in training
- Short feedback loops (can test immediately)
- Low-stakes failure modes (wrong output is obvious and recoverable)

**Low performance conditions:**
- Ambiguous requirements (the Devin Gap applies here)
- Complex interactions with existing systems
- Novel domains outside training data (frontier research, proprietary systems, legacy code)
- Long feedback loops (bugs only surface at runtime or in production)
- High-stakes failure modes (security, financial, safety-critical)

The mistake most developers make when evaluating vibe coding: they test it on high-performance conditions (simple, new, testable) and generalize to all conditions. The cases where vibe coding breaks are the cases where you need it most — complex, ambiguous, high-stakes.

---

## 2.4 The Expert-Novice Productivity Gap

METR's study found an overall 19% productivity decrease in AI-assisted developers. But the breakdown by experience level tells a more nuanced story:

Developers in the top quartile of experience showed smaller slowdowns or modest gains. Developers in the bottom quartile showed the largest slowdowns. The METR finding may be mostly a novice effect: experienced developers are adapting their workflows effectively; novice developers are not.

This creates an uncomfortable prediction: AI coding tools may **increase** the productivity gap between experienced and inexperienced developers, at least in the medium term. Experienced developers can verify AI output quickly; novices cannot. Experienced developers can catch AI-introduced bugs; novices cannot. Experienced developers know when to trust AI and when to be skeptical; novices use it uniformly.

If this is correct, the skills bottleneck is not "learning to use AI tools" but "having enough domain knowledge to evaluate AI output." The tool is secondary; the judgment is primary.

---

## Key Concepts

- **Origin:** Karpathy, February 2, 2025; Collins Word of the Year 2025
- **Three variants:** Novice (high risk), Expert (moderate risk), Collaborative (depends on review quality)
- **Performance envelope:** Defined tasks, greenfield work, short feedback loops — degrades on ambiguity and complexity
- **Expert-novice gap:** AI tools may amplify existing skill differences, not reduce them

---

## Hands-On Exercise

**Exercise 2.1: Map your vibe coding variant**

Audit your last 10 AI-assisted coding sessions. For each, classify:
- Which variant were you using? (Novice / Expert / Collaborative)
- Was the task inside or outside the high-performance envelope?
- What was the outcome? Did you review the output? Did you understand it?

This is data about your own patterns, not about AI tools in general.

**Exercise 2.2: The verification test**

Pick an AI-generated function you used recently. Without running it:
1. Describe in plain English what it does
2. Identify the input validation (or note its absence)
3. Describe what happens at the boundary cases (empty input, max values, malformed input)
4. Identify any external dependencies and note what happens if they fail

If you can't answer these questions, you were novice vibe coding regardless of your experience level.

---

## Discussion Questions

1. Karpathy coined the term but is an expert practitioner. The term then got applied to novice practice. Is this a problem with the term, or a reflection of something real about both practices?

2. If vibe coding "mostly works" for individual projects but produces unmaintainable code at scale, is it net positive or negative for the industry? What's the right counterfactual?

3. Collins naming vibe coding Word of the Year reflects mainstream adoption of the concept. What does it mean for a technical practice to enter mainstream discourse? Does it change the practice?

4. The expert-novice gap hypothesis suggests AI tools benefit experienced developers more than novice ones. If true, what are the implications for CS education and developer onboarding?

---

## References

- Karpathy, A. (February 2, 2025). "Vibe coding" post, X.
- Collins Dictionary Word of the Year 2025.
- METR productivity RCT, 2026.
- Devin performance studies, Cognition AI (January 2026).
