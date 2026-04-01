# Module 6: Code Quality in the AI Era

---

## Learning Objectives

By the end of this module, you will be able to:
1. Explain how AI-generated code changes the code quality landscape
2. Apply governance frameworks that actually improve code quality (not theater)
3. Identify AI-specific code patterns that standard linters miss
4. Design a review process that accounts for AI code failure modes

---

## 6.1 The Governance Gap

In 2025, Sonar analyzed 2.3 million code reviews across 4,000 organizations. The headline finding:

- Teams with AI coding tools but **no governance**: issues increased **1.7x** vs. pre-AI baseline
- Teams with AI coding tools and **governance**: issues decreased **0.3x** vs. pre-AI baseline

The governance delta — 1.7x worse without, 0.3x better with — is a 2x difference in code quality outcomes. AI tools are a multiplier of existing practices. Good practices get better. Absent practices get substantially worse.

The word "governance" is doing work here. It doesn't mean bureaucracy. It means: mandatory human review of AI output, checklists tuned to AI failure modes, and automated scanning calibrated to the patterns AI produces.

---

## 6.2 AI-Specific Failure Modes

AI-generated code fails in characteristic ways that differ from human-written code. Standard code review finds human bugs; you need an augmented process for AI bugs.

### Confidently Incorrect Logic

Human code tends to fail loudly — syntax errors, obvious logic gaps, runtime exceptions at obvious points. AI code tends to fail quietly — syntactically correct, stylistically idiomatic, logically wrong in subtle ways.

Example: An AI-generated rate limiter that correctly implements token bucket logic but initializes the bucket size from an environment variable that defaults to 0 in production, effectively disabling rate limiting silently.

The review question: Does this code do what the task required, or does it do what a plausible implementation of the task would do?

### Security Pattern Misapplication

AI correctly identifies which security pattern to apply but applies it incorrectly.

Common instance: parameterized query usage. AI will correctly use parameterized queries for the primary query in a function — because it has seen this pattern extensively. But if the function has a secondary query (for logging, for example), AI may fail to parameterize it. The function is "mostly" safe and passes cursory review.

The review question: Is the pattern applied consistently throughout the function, or only in the obvious places?

### Test Coverage Illusion

AI-generated tests achieve high line coverage but low behavioral coverage. They test the happy path extensively; edge cases not at all.

Specific patterns to watch for in AI-generated test suites:
- All tests use the same valid input type (never tests `None`, `""`, negative numbers, or other edge cases)
- Tests verify that functions run without error, not that they produce correct output
- No tests for failure modes (what happens when the DB is down, when the API returns 429, when the input is malformed)
- No tests for race conditions or concurrent access (if relevant)

The review question: Do these tests describe the behavior of the function, or just demonstrate that it doesn't crash on typical input?

### Dependency Chain Expansion

AI recommends importing dependencies for small tasks rather than implementing minimal solutions.

Example: asking AI to parse a date string produces code that imports `arrow` (a 500KB dependency) rather than using stdlib `datetime`. The `arrow` solution is more readable; it's also a new dependency with its own vulnerability surface and maintenance burden.

The review question: Is this dependency justified by what it adds, or could stdlib handle it?

### Hallucinated API Usage

AI will confidently use library APIs that don't exist, are deprecated, or behave differently than the code assumes. This is most common with:
- Less popular libraries (lower training data coverage)
- Recent API changes (training data cutoff)
- Platform-specific behaviors (works on Linux, different on Windows)

The review question: Does this code reference APIs I've verified exist and work as assumed?

---

## 6.3 Governance That Works

### The AI Code Review Checklist

Not a generic checklist — a checklist specifically designed for AI-generated code:

**Logic verification**
- [ ] I understand what this code does, not just what it's supposed to do
- [ ] I have traced the execution path for at least the two most likely inputs
- [ ] The output matches the spec under both happy path and error conditions

**Security-specific**
- [ ] All user input is validated at the boundary
- [ ] Security patterns (auth, parameterization, encryption) are applied consistently, not just in the obvious places
- [ ] No credentials, keys, or secrets in the code
- [ ] Dependencies added are justified; no new attack surface without justification

**Test coverage**
- [ ] Tests cover edge cases: empty input, null/None, boundary values, error conditions
- [ ] Tests verify correct output, not just no-exception
- [ ] If concurrent access is possible, concurrency is tested

**Dependencies**
- [ ] New dependencies are in the approved list or explicitly reviewed
- [ ] No dependency added for functionality achievable with stdlib

**Maintainability**
- [ ] A developer unfamiliar with this code can understand it without documentation
- [ ] Error messages are informative (not generic exceptions)

### Automation Augmentation

Standard linters (ruff, pylint, eslint) are not calibrated to AI failure modes. Add:

**Security scanners:** `bandit` (Python), `semgrep` with rulesets tuned to AI-generated patterns. Key rule: flag any function that uses parameterized queries in some paths but not others.

**Dependency auditing:** `pip-audit` or `safety` on every PR. New dependencies trigger a review step, not just a vulnerability scan.

**Test coverage with behavioral requirements:** Line coverage is necessary but not sufficient. Require coverage of at least 2 error paths per function.

---

## 6.4 The Verification-Speed Tradeoff

The METR study found that AI-assisted developers spent significant time verifying AI output — enough time to offset generation speed. This is the verification-speed tradeoff, and it's not a problem to be solved. It's a tradeoff to be managed.

The tradeoff has an optimal point. Under-verification (accepting AI output with minimal review) produces the 1.7x issue increase. Over-verification (checking every line as carefully as you'd write it yourself) eliminates the speed gain.

The optimal verification depth depends on:
- **Code criticality:** Authentication and payment code needs deep verification. Test utilities need less.
- **Domain familiarity:** Code in your core domain is faster to verify (you know what correct looks like). Code in unfamiliar domains takes longer.
- **Task complexity:** Simple, contained functions are faster to verify than complex, cross-cutting ones.
- **AI confidence signals:** Hedged, qualified AI output ("there may be edge cases I'm not handling") warrants more verification than confident output. (Paradoxically, confident AI output often deserves *more* scrutiny, not less.)

---

## 6.5 Organizational Governance

Individual developer practices matter, but organizational practices create the floor.

**Required elements:**
1. **Policy:** AI-generated code requires human review. This sounds obvious; many teams don't have it explicitly stated.
2. **Tooling:** The review tooling includes AI-specific checks (the checklist, the automated scans).
3. **Accountability:** If AI-generated code causes an incident, the incident review examines the review process, not just the code.
4. **Learning:** AI-specific failure modes are documented and shared. When someone finds a novel AI failure mode, it gets added to the review checklist.

**Cultural element:** The goal is not to be suspicious of AI-generated code. The goal is to verify it appropriately given its failure modes — the same way you'd have different verification processes for, say, code from an intern vs. code from a senior engineer you deeply trust.

---

## Key Concepts

- **Governance gap:** 1.7x worse without governance, 0.3x better with it (Sonar, 2025)
- **AI failure modes:** Quiet logic errors, security pattern misapplication, coverage illusion, dependency expansion, hallucinated APIs
- **AI code review checklist:** Specifically designed for AI failure modes, not generic best practices
- **Verification-speed tradeoff:** Has an optimal point that depends on code criticality, domain familiarity, and task complexity
- **Organizational governance:** Policy + tooling + accountability + learning

---

## Hands-On Exercise

**Exercise 6.1: AI failure mode audit**

Find three pieces of AI-generated code you've shipped in the last month. Apply the AI code review checklist retroactively. Did you find anything? What does this tell you about your current verification process?

**Exercise 6.2: Build your checklist**

Design a code review checklist for your specific domain (your team's codebase, your primary technology, your key risk areas). Start from the generic checklist above; customize for what AI fails at in your context.

**Exercise 6.3: Test coverage assessment**

Take an AI-generated test suite and audit its behavioral coverage:
- What edge cases are missing?
- What error paths are not tested?
- What failure modes does the test suite tell you nothing about?

---

## Discussion Questions

1. The Sonar data shows a 2x difference in code quality outcomes based on governance. What does this imply for organizations that have adopted AI tools without a corresponding governance update?

2. AI code fails quietly (syntactically correct, logically wrong). Human code fails loudly (more likely to produce obvious errors). Is quiet failure better or worse than loud failure in a production system?

3. The verification-speed tradeoff has an optimal point. How would you empirically find that optimal point for your team?

4. "AI tools are a multiplier of existing practices." If your team's existing practices are poor, AI tools make them worse. What's the responsible approach to AI tool adoption in an organization with weak engineering practices?

---

## References

- Sonar Code Quality in the AI Era report, Q4 2025
- METR productivity study, 2026
- OWASP AI Security and Privacy Guide, 2025
- GitHub Advanced Security documentation on AI-assisted code scanning
