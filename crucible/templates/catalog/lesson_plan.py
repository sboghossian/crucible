"""Lesson plan design team — Education."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="lesson_plan",
    description="Creates a comprehensive lesson plan with learning objectives, activities, differentiation strategies, and assessment.",
    category="Education",
    tags=["lesson plan", "teaching", "education", "k12", "higher ed", "pedagogy"],
    agents=[
        AgentSpec(
            name="Curriculum Aligner",
            role="Standards alignment and learning objective specialist",
            instructions=(
                "You are a curriculum specialist. For the given topic and grade level, produce: "
                "alignment to relevant educational standards (Common Core, NGSS, or equivalent), "
                "3-5 specific, measurable learning objectives (Bloom's taxonomy verbs), "
                "prerequisite knowledge students need, "
                "connections to prior and future lessons, "
                "and cross-curricular connections (how does this link to other subjects?)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Instructional Designer",
            role="Lesson structure and engagement specialist",
            instructions=(
                "You are an instructional designer. Build a detailed lesson plan: "
                "duration (e.g., 50-minute period), "
                "warm-up / hook activity (5 min) with purpose, "
                "direct instruction phase with key points and examples, "
                "guided practice activity (collaborative or individual), "
                "independent practice / application task, "
                "closure activity (exit ticket, discussion, self-assessment), "
                "and materials list (readings, manipulatives, technology, handouts)."
            ),
            config=AgentConfig(max_tokens=3500),
        ),
        AgentSpec(
            name="Differentiation Specialist",
            role="Inclusive instruction and UDL specialist",
            instructions=(
                "You are a differentiation and Universal Design for Learning (UDL) specialist. Produce: "
                "modifications for students with IEPs or 504 plans, "
                "scaffolds for English Language Learners, "
                "enrichment challenges for advanced learners, "
                "multiple means of engagement (choice boards, flexible grouping), "
                "multiple means of representation (visual, auditory, kinesthetic), "
                "and formative check-in strategies to identify who needs additional support mid-lesson."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
        AgentSpec(
            name="Assessment Designer",
            role="Formative and summative assessment specialist",
            instructions=(
                "You are an assessment design expert. Create: "
                "3 formative assessment strategies for during the lesson, "
                "an exit ticket (3 questions: recall, understanding, application), "
                "a summative assessment option (quiz, project, performance task), "
                "a rubric for the main student activity, "
                "teacher reflection prompts for after the lesson, "
                "and data-use suggestions (what to look for in student work, how to adjust next lesson)."
            ),
            config=AgentConfig(max_tokens=2500),
        ),
    ],
    debate_topics=[
        "What instructional approach will produce the deepest learning for this concept?",
        "Direct instruction with guided notes (efficient, clear, low ambiguity)",
        "Discovery learning (productive struggle, longer retention)",
        "Flipped instruction (consume content at home, apply in class)",
        "Project-based learning (authentic task, intrinsic motivation)",
    ],
    expected_outputs=[
        "Complete lesson plan with timing breakdown",
        "Standards alignment",
        "3-5 measurable learning objectives",
        "Differentiation strategies for three learner profiles",
        "Exit ticket with 3 questions",
        "Summative assessment with rubric",
        "Materials list",
        "Teacher reflection prompts",
    ],
))
