# Crucible Launch Playbook

*GitHub star strategy and community launch plan.*

---

## The Core Hypothesis

Most developer tools are launched wrong. They lead with features, not with the feeling. The GitHub landing page has maybe 8 seconds to communicate "this is worth my time" — and the way to spend those 8 seconds is with a demo GIF that makes someone think "I want that."

Crucible's hook is specific and visual: four AI personas arguing about a real decision in real time. That's the thing people will share. Everything else is secondary.

---

## 1. GitHub Page Optimization

### The Demo GIF Rule

A demo GIF must appear **in the first screenful** of the README — before any prose, before any architecture diagram, before any installation instructions. This is non-negotiable.

The GIF shows:
1. User runs `python -c "..."` with a short debate invocation (3 lines)
2. Four personas appear sequentially, each with a distinct name and position
3. Cross-examination appears: one persona challenging another
4. A winner is announced with a numeric score and one-sentence decision

**Target runtime:** 30-45 seconds. Long enough to convey the concept; short enough that someone watches the whole thing.

**Technical requirements:**
- Recorded in a terminal with dark background and clean font
- Color-coded by persona (PRAGMATIST in green, VISIONARY in cyan, SKEPTIC in yellow, USER ADVOCATE in magenta)
- Final frame holds for 3 seconds on the winner announcement
- Loopable — the GIF loops seamlessly

Tools: `asciinema` for recording, `agg` for conversion to GIF, or `terminalizer`.

---

### The 5-Minute Install Standard

The standard for developer tool READMEs: a user who has Python 3.11+ and an Anthropic API key should go from `pip install` to working output in **under 5 minutes**.

The three-command quick start:

```bash
pip install crucible-ai
export ANTHROPIC_API_KEY=sk-...
python -c "
import asyncio; from crucible import Orchestrator
async def main():
    o = Orchestrator()
    r = await o.standalone_debate(
        topic='Should we migrate to microservices?',
        options=['yes now', 'no', 'strangler fig pattern'],
        context='3 engineers, 50k DAU, 4-year-old monolith'
    )
    print(f'Winner: {r.winner} ({r.winner_score:.1f}/10)')
    print(r.decision)
asyncio.run(main())
"
```

Every word in this command matters. No boilerplate imports the user doesn't need. No multi-step setup. One block that can be copy-pasted from the README.

**The 5-minute clock starts the moment they hit install. It ends when they see `Winner:` in their terminal.**

---

### README Structure (Ordered for Conversion)

1. **Badge row** (license, Python version, PyPI version, test status)
2. **One-sentence tagline** ("Most multi-agent frameworks are demos. Crucible is a research instrument.")
3. **Demo GIF** ← conversion happens here
4. **3-line quick start** ← retention happens here
5. The Problem (2-3 sentences)
6. The Debate Council explanation (table of personas + round structure)
7. Real debate transcript (the naming example)
8. Full architecture diagram (Mermaid)
9. Agent reference table
10. Installation and configuration
11. Contributing / roadmap

Do not reorder this. The ordering is not aesthetic — it's a conversion funnel.

---

## 2. Hacker News Launch

### Timing: Tuesday 8 AM PT

Post to Hacker News **Tuesday at 8:00 AM Pacific Time**. The data on HN timing is consistent: Tuesday through Thursday mornings (Pacific) maximize the time a post has to accumulate upvotes before the West Coast day ends. Monday posts compete with weekend-accumulated content. Friday posts die over the weekend.

8 AM PT is when the East Coast is in mid-morning and the West Coast is just starting. Posts that get early upvotes in the first hour compound.

### Show HN vs Ask HN

**Show HN** is the correct submission type. "Show HN: Crucible — a multi-agent research framework with a 4-persona adversarial Debate Council."

Title rules:
- Lead with "Show HN:"
- Name the project
- One concrete, specific claim that is true and surprising
- No hype words ("revolutionary", "blazing fast", "game-changing")

Good: "Show HN: Crucible — multi-agent debates where the best argument wins, not consensus"
Bad: "Show HN: Crucible — the AI framework that will change how you make decisions"

### The Launch Comment

Post a comment immediately after submission with:
1. The problem you're solving (2 sentences)
2. The key design decision that sets this apart (the Debate Council concept)
3. What you'd most like feedback on
4. An honest assessment of current limitations

Do not oversell. HN readers reward honesty about limitations more than claims of perfection. Saying "it's expensive on Opus because we haven't implemented caching yet, that's the top roadmap item" is better than pretending the limitation doesn't exist.

### The First 2 Hours Rule

**Respond to every comment in the first 2 hours.** Every comment. Even if it's just "good point, filed as an issue." This is not politeness — it's mechanics. HN's algorithm factors engagement. Comments with replies generate sub-threads. Sub-threads keep the post active longer.

After 2 hours, prioritize technical comments (challenges, questions, suggestions) over praise. Technical engagement is more valuable for the product than compliments.

### What to Expect

A well-executed Show HN with a novel-but-real concept typically:
- Front page for 6-12 hours if it breaks ~100 upvotes in the first 2 hours
- 200-500 GitHub stars from an HN front page post
- 10-30 substantive comments worth reading carefully
- 3-7 pull requests within 48 hours
- 1-2 "this is what I'm building too, let's talk" DMs

---

## 3. Community Targets

### Primary Communities (launch week)

| Community | Where | Approach |
|-----------|-------|----------|
| **Hacker News** | Show HN | Main launch post |
| **r/MachineLearning** | Reddit | Post the research findings (METR study, SWE-bench contamination), link Crucible as the practical outcome |
| **r/LocalLLaMA** | Reddit | Frame around "you can run debates with any model, here's how" |
| **AI Twitter/X** | X | Demo GIF thread, tag Karpathy (coined vibe coding), tag researchers whose work is cited |
| **LangChain Discord** | Discord | Post in #show-and-tell, explain how Crucible complements LangGraph |

### Secondary Communities (weeks 2-4)

| Community | Angle |
|-----------|-------|
| **Towards Data Science / Medium** | "The case for adversarial AI review" — thought leadership post with Crucible as the practical example |
| **Dev.to** | Tutorial post: "Building your first AI debate with Crucible" |
| **Python Discord** | Show in #projects |
| **IndieHackers** | Frame as OSS + course bundle: "I built a research tool and turned the findings into a course" |
| **AI Tinkerers (local meetups)** | Live demo at a meetup — debates are compelling in person |

### Influencer Outreach

Do not mass-DM. Identify 5-7 people whose work Crucible builds on or references:
- Researchers whose papers are cited in the course
- Engineers who have written about multi-agent system limitations
- Developers who have open-sourced multi-agent tools

Personal, specific outreach: "I read your post about [specific thing]. Crucible's Debate Council is partly an attempt to address the limitation you identified. Would you be willing to take a look?"

---

## 4. The 30-Day Plan

### Week 1: Launch

**Day 1 (Tuesday):** HN launch. Respond to all comments. Monitor stars. Fix any installation bugs that surface.

**Day 2-3:** Write up the HN response. Post to r/MachineLearning and r/LocalLLaMA with the research angle. Continue responding to late HN comments.

**Day 5-7:** Process the feedback. What did people ask for that you didn't have? What did they misunderstand? These are either product gaps or documentation gaps.

### Week 2: Content

Post the first substantive piece of content: "Why multi-agent consensus is a problem and what adversarial review does about it." This is not marketing copy — it's the intellectual case for the design decision. Link to the research docs in the Crucible repo.

Release the first module of the course for free. Use this to validate interest in the educational angle.

### Week 3: Community Building

Start a GitHub Discussions thread: "What decisions are you running through the Debate Council?" Seed it with 3 examples from your own use.

Respond to all open issues. Every issue response should include either a fix, an explanation, or an honest "this is on the roadmap."

### Week 4: Iteration

By day 30, you should have:
- 200+ GitHub stars minimum (if HN front page)
- 5+ substantive GitHub issues or PRs from community
- A clear signal on whether the course angle has traction
- 1-2 features added based on community feedback

The 30-day goal is not a star count. It's: **does the community understand what Crucible is, and are people using it?** Stars are a proxy. Real usage data (GitHub traffic, API call volume if you instrument it) is the signal.

---

## 5. What Not to Do

**Don't buy ads.** Developer tools don't convert on paid ads. Word-of-mouth and organic discovery is the only channel that works.

**Don't chase every community simultaneously.** Launch into one community at a time, in the order above. Spreading thin produces mediocre engagement everywhere instead of excellent engagement somewhere.

**Don't hide the limitations.** The most credible thing you can say is "here's what it doesn't do yet, here's why, here's when we expect to fix it." Developers respect honesty about limitations because most product launches are dishonest about them.

**Don't pivot based on 48-hour feedback.** The feedback in the first 48 hours is biased toward people who comment on HN — a specific demographic with specific preferences. Collect it, but weight it carefully. If 10 people independently ask for the same thing over 2 weeks, that's a signal. If 1 person asks for something forcefully in the first hour, that's noise.

**Don't launch on a Monday.** Or a Friday. Or over a holiday. These are not opinions — the data is clear.
