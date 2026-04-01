# Module 9: Open Source Strategy

---

## Learning Objectives

By the end of this module, you will be able to:
1. Articulate why open source is a distribution strategy, not just a licensing choice
2. Design a GitHub presence optimized for developer discovery and trust
3. Build a launch strategy with specific timing, targeting, and response tactics
4. Distinguish between vanity metrics (stars) and signal metrics (active users, contributors)

---

## 9.1 Open Source as Distribution

The fundamental insight: open source is not primarily a licensing choice or a philosophical stance. It's a distribution channel.

For developer tools, the distribution question is: how does a developer who would benefit from your tool find out it exists? The answer in 2026:
1. **Word of mouth from peers** (most trusted, hardest to engineer)
2. **GitHub discovery** (search, trending, related repos)
3. **Hacker News / Reddit** (high reach, one-shot)
4. **Twitter/X** (high velocity, short half-life)
5. **Blog posts and tutorials** (durable, builds over time)

Open source makes all five channels more accessible: it lets developers try before committing, enables contributors who become advocates, and signals that you're not hiding anything.

---

## 9.2 The GitHub Page as a Conversion Funnel

A developer lands on your GitHub page from search, a shared link, or a news post. They have about 8 seconds to decide if this is worth their time.

The README is a conversion funnel, not a documentation dump. Order it for conversion:

**First screenful (must convert here):**
- Name and one-sentence description
- Demo GIF or screenshot
- Badge row showing health indicators

**Second screenful (must retain here):**
- Quick start (3 commands max)
- The problem in 2-3 sentences

**Everything else:**
- Detailed explanation
- Architecture
- Full documentation

The most common mistake: README starts with backstory, philosophy, or architecture. These are good content for people who are already interested. They are not conversion content.

### The Demo GIF Rule

A well-made demo GIF converts skeptics that no amount of prose will convert. The gif shows — it doesn't explain. In Crucible's case: watch the personas argue in real time. See the scoring. See the winner declared. You immediately understand what the product does.

**GIF best practices:**
- Record in a clean terminal (dark background, readable font)
- Show the full cycle from command to output
- Highlight the most surprising/compelling moment
- 30-45 seconds maximum
- Loop smoothly

---

## 9.3 Documentation as Trust Signal

Documentation quality signals team quality. A project with comprehensive, accurate docs demonstrates that the maintainers care about users, not just contributors. It also lowers the barrier to contribution — you can't contribute to code you don't understand.

**Minimum viable documentation:**
1. **README:** First impression, quick start, architecture overview
2. **API reference:** Every public function, class, and parameter
3. **Examples:** Working code that demonstrates real use cases
4. **Contributing guide:** How to get from "interested" to "first PR merged"

**Documentation red flags:**
- "Coming soon" in the API reference
- Examples that don't work with the current version
- Contributing guide that is just "open a PR"
- No explanation of error messages

For Crucible specifically: the research documents in `docs/` serve a dual purpose — documentation and intellectual proof of work. They demonstrate that the project is grounded in real research, not just engineering intuition.

---

## 9.4 The Launch Strategy

### Hacker News (Show HN)

The highest-signal community for developer tool launches. A front-page HN post can generate 200-500 stars in a day.

**Timing:** Tuesday-Thursday, 8:00 AM Pacific. This is not folklore — post timing affects initial velocity, and initial velocity affects front page probability.

**Title format:** `Show HN: [Name] — [specific, concrete, true claim]`

Good: "Show HN: Crucible — multi-agent debates where the best argument wins, not consensus"
Bad: "Show HN: I built an AI framework" (vague), "Show HN: Crucible is the future of AI development" (hype)

**The critical first 2 hours:** Respond to every comment. Every response extends the thread. Thread activity signals to HN's algorithm that the post has ongoing engagement.

**What to expect from a successful HN launch:**
- Front page: 6-12 hours (if you break ~100 upvotes early)
- Stars: 200-500 from the HN post alone
- Comments: 10-30 substantive ones worth reading
- PRs: 3-7 within 48 hours
- Email/DMs: 1-3 "let's talk" from people building related things

### Reddit

Different dynamics than HN. More forgiving, more community-specific.

**r/MachineLearning:** Lead with the research angle. The METR productivity finding, the SWE-bench contamination story, the Devin Gap — this community cares about rigorous analysis. Crucible is positioned as a research instrument; lead with the research.

**r/LocalLLaMA:** Frame around "you can run debates with any model." This community cares about local/open-source options. If Crucible supports local models, that's the lede.

**r/Python:** Technical implementation post. Show interesting code patterns.

**Post format for Reddit:** Long-form is better than short-form. Reddit readers engage more with posts that have substance. Don't just drop a link.

### Twitter/X

High velocity, short half-life. A tweet has a 24-48 hour window before it's gone from feeds.

**Thread format works better than single tweet.** Show 3-4 steps of the demo with screenshots. End with a link.

**Tagging strategy:** Tag researchers whose work you cite. Not as a marketing tactic — genuinely, to say "your work influenced this." Most researchers appreciate the reference and may amplify.

---

## 9.5 Community Building After Launch

Stars are not the goal. Active users are the goal. The difference: a star takes 1 second. Active use takes hours. The ratio tells you how many people found it interesting vs. how many found it useful.

**Retention levers:**

*GitHub Discussions* — start a thread with a real question (not "share your use cases!"). Seed it with 3-4 substantive examples. Make it easy for someone to participate without having a "use case" ready.

*Issue responsiveness* — time-to-first-response on new issues is one of the strongest predictors of whether a first-time contributor becomes a repeat contributor. A response within 24 hours is excellent; within 72 hours is acceptable; more than a week and you're losing potential contributors.

*Release cadence* — irregular releases are a community killer. Even a minor release every 2-4 weeks signals that the project is alive. Use release notes to communicate directly with users about what's changing and why.

**The contributor funnel:**
1. User (uses the tool)
2. Reporter (files an issue or discussion post)
3. Commenter (engages with issues/PRs from others)
4. Contributor (submits a PR)
5. Maintainer (takes on ongoing responsibility)

Most projects lose people at step 2 → 3. Make it easy to engage without submitting code: good documentation discussions, issue labels that invite comment, explicit "help wanted" labels.

---

## 9.6 Vanity vs. Signal Metrics

| Vanity metric | Signal metric | Why |
|---------------|---------------|-----|
| GitHub stars | Monthly active users | Stars = interest; MAU = value |
| Fork count | PRs from forks | Forks = exploration; PRs = contribution |
| Clone count | Installations that run | Clones = curiosity; runs = use |
| Social media impressions | Click-through rate | Reach ≠ resonance |
| Total contributors | Repeat contributors | One PR ≠ ongoing engagement |

Track the signal metrics. Use vanity metrics only as top-of-funnel leading indicators.

---

## Key Concepts

- **Open source as distribution:** Not just licensing — the most accessible multi-channel distribution strategy for developer tools
- **README as funnel:** Ordered for conversion, not comprehensiveness; demo GIF in first screenful
- **HN timing:** Tuesday-Thursday 8 AM PT; respond to all comments in first 2 hours
- **Community retention:** Discussion threads, issue responsiveness, release cadence
- **Signal vs. vanity:** MAU > stars; repeat contributors > contributor count

---

## Hands-On Exercise

**Exercise 9.1: README audit**

Find a developer tool with 1,000+ stars. Audit its README as a conversion funnel:
- What's in the first screenful?
- How long to the first working output?
- Is the problem stated before the solution?
- What would you change?

**Exercise 9.2: Launch plan**

Design a launch plan for Crucible (or a project of your own) that covers:
- Timing and platform sequence
- Title and description variations for each platform
- First-2-hours response strategy
- 30-day retention plan

**Exercise 9.3: Contribution ladder**

Map the contribution ladder for an open-source project you use. Where does it break down? What would make it easier to move from "user" to "contributor"?

---

## Discussion Questions

1. The launch playbook specifies Tuesday at 8 AM PT for HN. How would you test whether this actually matters for Crucible specifically? What would the experiment be?

2. "Respond to every comment in the first 2 hours." What's the cost? What's the benefit? Is this sustainable past launch week?

3. Stars are a vanity metric; MAU is a signal metric. But most open-source tools can't easily measure MAU. What are practical proxies that you could track without instrumenting user behavior?

4. The research documents in `docs/` serve as intellectual proof of work. Does this change how you'd evaluate the project relative to one with no research documentation?

---

## References

- Crucible launch playbook: [docs/launch-playbook.md](../docs/launch-playbook.md)
- HN post timing analysis (multiple community analyses, widely available)
- "Roads and Bridges: The Unseen Labor Behind Our Digital Infrastructure" (Ford Foundation, 2016) — foundational analysis of open source sustainability
