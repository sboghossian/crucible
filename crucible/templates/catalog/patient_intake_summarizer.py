"""Patient intake summarization team — Healthcare & Wellness."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="patient_intake_summarizer",
    description="Structures and summarizes patient intake information for clinical review, flagging key risks and care priorities.",
    category="Healthcare & Wellness",
    tags=["healthcare", "patient intake", "clinical", "medical summary", "triage"],
    agents=[
        AgentSpec(
            name="Medical Historian",
            role="Medical history extraction and organization specialist",
            instructions=(
                "You are a clinical documentation specialist. Structure the patient intake data into: "
                "chief complaint (CC) in patient's own words, "
                "history of present illness (HPI) using OLDCARTS framework "
                "(Onset, Location, Duration, Character, Aggravating/Alleviating factors, Radiation, Timing, Severity), "
                "past medical history (PMH) with active conditions, "
                "surgical history, "
                "family history (relevant first-degree relatives), "
                "social history (smoking, alcohol, drug use, occupation, living situation). "
                "Flag any missing critical history elements. Educational purposes only — not for clinical use without physician review."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Medication Reviewer",
            role="Medication reconciliation and interaction flag specialist",
            instructions=(
                "You are a clinical pharmacist assistant. From the medication list, produce: "
                "structured medication list (drug, dose, frequency, indication, prescriber), "
                "allergies and adverse reaction history (with reaction type: allergy vs. intolerance), "
                "high-alert medication flags (anticoagulants, insulin, narrow therapeutic index drugs), "
                "potential drug-drug interaction flags for review by clinical staff, "
                "and OTC/supplement/herbal medication list (often omitted but clinically relevant). "
                "Note: All findings require physician or pharmacist verification."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Risk Screener",
            role="Clinical risk stratification and safety screening specialist",
            instructions=(
                "You are a clinical risk assessment assistant. Screen for: "
                "fall risk factors (age, mobility, medications, prior falls), "
                "suicide and self-harm risk indicators (PHQ-9 scores, stated ideation, history), "
                "substance use disorder indicators, "
                "social determinants of health (SDOH) flags (food insecurity, housing instability, transportation), "
                "infection control flags (recent travel, immunocompromised status, communicable disease exposure), "
                "and advance directive status (DNR, POA, living will). "
                "All flags require clinician review before action."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Visit Summarizer",
            role="Clinical summary and care priority synthesizer",
            instructions=(
                "You are a clinical summary writer. Produce: "
                "one-page visit summary for clinical team review, "
                "prioritized problem list (active issues ranked by acuity), "
                "recommended care priorities for this visit (top 3), "
                "preventive care gaps (vaccines, screenings overdue based on age/sex/history), "
                "follow-up items from prior visits (unresolved issues), "
                "and patient communication summary (how to explain the visit plan in plain language). "
                "For clinical team use only; requires physician review and validation."
            ),
            config=AgentConfig(max_tokens=3000),
        ),
    ],
    debate_topics=[
        "What should be the primary focus of this patient visit given competing priorities?",
        "Address acute chief complaint first (immediate concern drives patient attendance)",
        "Prioritize chronic disease management (long-term outcomes have greater impact)",
        "Focus on preventive care gaps (highest ROI per clinical minute)",
        "Address SDOH barriers first (social factors undermine all clinical interventions)",
    ],
    expected_outputs=[
        "Structured HPI using OLDCARTS framework",
        "Medication reconciliation list with high-alert flags",
        "Risk stratification summary",
        "Prioritized problem list",
        "One-page visit summary for clinical team",
        "Preventive care gaps list",
        "Patient-facing plain-language summary",
    ],
))
