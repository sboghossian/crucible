"""Symptom research and clinical information team — Healthcare & Wellness."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="symptom_checker_research",
    description="Researches medical literature to produce differential considerations, specialist recommendations, and patient question guides for symptoms. Not medical advice.",
    category="Healthcare & Wellness",
    tags=["healthcare", "symptoms", "medical research", "patient education", "health information"],
    agents=[
        AgentSpec(
            name="Symptom Profiler",
            role="Symptom characterization and history specialist",
            instructions=(
                "You are a medical education researcher. For the described symptoms, create: "
                "a structured symptom questionnaire (onset, duration, severity, quality, location, radiation, "
                "aggravating and relieving factors, associated symptoms, temporal pattern), "
                "red flag symptom checklist (symptoms requiring emergency evaluation), "
                "relevant history questions (past medical history, medications, family history, social history), "
                "and a symptom severity self-assessment scale. "
                "IMPORTANT: This is educational information only. Always seek evaluation from a qualified healthcare provider."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Medical Researcher",
            role="Clinical literature and differential research specialist",
            instructions=(
                "You are a medical information researcher. For the described symptom profile, research: "
                "common causes to discuss with a doctor (organized from most to least common), "
                "less common but important causes the clinician may consider, "
                "red flag causes requiring urgent evaluation, "
                "related body systems involved, "
                "and typical diagnostic workup for this symptom pattern. "
                "This is for educational preparation only — differential diagnosis requires clinical evaluation. "
                "Always recommend professional medical evaluation."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Specialist Navigator",
            role="Healthcare navigation and specialist referral specialist",
            instructions=(
                "You are a healthcare navigation specialist. Recommend: "
                "initial point of care (primary care, urgent care, emergency department, telemedicine), "
                "specialist types who manage these symptoms (e.g., cardiologist, neurologist, gastroenterologist), "
                "questions to ask the primary care physician to ensure appropriate referral, "
                "how to prepare for the appointment (symptoms diary, medication list), "
                "and advocacy tips for getting thorough evaluation."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
        AgentSpec(
            name="Patient Educator",
            role="Layperson health literacy and question preparation specialist",
            instructions=(
                "You are a patient education specialist. Produce: "
                "10 questions to bring to the doctor's appointment, "
                "a symptom tracking journal template (date, severity, triggers, context), "
                "plain-language glossary for medical terms the patient may encounter, "
                "lifestyle modifications commonly recommended for these symptoms (sleep, diet, stress — general), "
                "and trusted resources for further reading (general health information guidance). "
                "Reinforce clearly: this is educational preparation, not a substitute for professional medical care."
            ),
            config=AgentConfig(max_tokens=2000),
        ),
    ],
    debate_topics=[
        "What level of urgency is appropriate for these symptoms?",
        "Seek emergency evaluation now (red flag symptoms present)",
        "Schedule urgent appointment within 24-48 hours",
        "Schedule routine appointment and monitor",
        "Watchful waiting with defined trigger criteria for escalation",
    ],
    expected_outputs=[
        "Structured symptom questionnaire",
        "Red flag symptoms checklist",
        "Educational overview of possible causes (for discussion with doctor)",
        "Specialist referral guide",
        "10 questions for the doctor visit",
        "Symptom tracking journal template",
        "Urgency assessment framework",
        "Trusted health information resources",
    ],
))
