"""Meeting preparation team — Personal Productivity."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="meeting_prep",
    description="Prepares thoroughly for any high-stakes meeting with research, agenda, talking points, and follow-up plan.",
    category="Personal Productivity",
    tags=["meeting", "preparation", "productivity", "negotiation", "presentation", "communication"],
    agents=[
        AgentSpec(
            name="Context Researcher",
            role="Meeting context and stakeholder intelligence specialist",
            instructions=(
                "You are a meeting preparation analyst. Gather and synthesize: "
                "meeting purpose and desired outcome (what does 'success' look like?), "
                "attendee profiles (role, priorities, communication style, past interactions), "
                "relationship dynamics (who has power, who are allies, who might resist?), "
                "recent relevant developments (company news, project updates, prior meeting outcomes), "
                "and your BATNA (Best Alternative to a Negotiated Agreement) if this is a negotiation."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Agenda Designer",
            role="Meeting structure and time allocation specialist",
            instructions=(
                "You are a meeting design specialist. Build: "
                "meeting agenda with time allocations for each item, "
                "pre-meeting materials to send (and how far in advance), "
                "icebreaker or opening question to set the tone, "
                "decision points that need resolution (vs. items that are just for information sharing), "
                "and a 'parking lot' protocol for out-of-scope items that arise."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
        AgentSpec(
            name="Message Strategist",
            role="Key messages and persuasion specialist",
            instructions=(
                "You are a strategic communication coach. Prepare: "
                "your 3 key messages (what you need the other party to understand, believe, or agree to), "
                "supporting evidence for each message (data, examples, stories), "
                "anticipated questions and responses, "
                "anticipated objections and responses, "
                "opening statement (first 60 seconds — set the frame), "
                "and a closing / call to action."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Follow-Up Planner",
            role="Action capture and accountability specialist",
            instructions=(
                "You are a meeting follow-up specialist. Design: "
                "meeting notes template (decisions made, action items with owners and due dates, open questions), "
                "follow-up email template to send within 24 hours, "
                "action item tracking system, "
                "escalation protocol if commitments aren't kept, "
                "and a 'what to do if the meeting goes off-track' contingency protocol."
            ),
            config=AgentConfig(max_tokens=1500),
        ),
    ],
    debate_topics=[
        "What is the optimal meeting format for achieving the stated objective?",
        "Live synchronous (complex negotiation, relationship-building, creative problem-solving)",
        "Async collaboration (document review, data decisions, information sharing — don't need a meeting)",
        "Hybrid: async pre-work + short synchronous decision point",
    ],
    expected_outputs=[
        "Meeting agenda with time allocations",
        "Attendee profile summaries",
        "3 key messages with supporting evidence",
        "Anticipated objections and responses",
        "Opening statement (60 seconds)",
        "Meeting notes template",
        "24-hour follow-up email template",
    ],
))
