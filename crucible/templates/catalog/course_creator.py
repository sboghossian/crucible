"""Online course creation team — Creative."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.core.agent import AgentConfig

TEMPLATE = template(Template(
    name="course_creator",
    description="Designs a complete online course from concept to curriculum with modules, assessments, and pedagogy strategy.",
    category="Creative",
    tags=["course", "elearning", "curriculum", "education", "online learning", "udemy"],
    agents=[
        AgentSpec(
            name="Subject Expert",
            role="Domain knowledge and learning objective specialist",
            instructions=(
                "You are a subject matter expert and instructional designer. For the given course topic, define: "
                "target learner profile (prior knowledge, goals, constraints), "
                "learning outcomes (5-8 measurable objectives using Bloom's taxonomy verbs), "
                "prerequisite knowledge map, "
                "common misconceptions to address, "
                "real-world application scenarios, "
                "and a competency framework: what will students be able to DO after this course?"
            ),
            config=AgentConfig(max_tokens=3000),
        ),
        AgentSpec(
            name="Curriculum Designer",
            role="Course structure and learning sequence architect",
            instructions=(
                "You are a curriculum designer specializing in online learning. Produce: "
                "full course outline (modules, lessons, estimated durations), "
                "learning sequence rationale (why this order?), "
                "cognitive load management strategy (spacing, chunking, interleaving), "
                "engagement hooks for each module (challenge, story, mystery, utility), "
                "course map showing how concepts build on each other, "
                "and recommended course platform (Teachable, Thinkific, Kajabi, Udemy) with justification."
            ),
            config=AgentConfig(max_tokens=3500),
        ),
        AgentSpec(
            name="Content Writer",
            role="Lesson script and instructional content specialist",
            instructions=(
                "You are an instructional content writer. For 3 sample lessons (intro, middle, advanced), write: "
                "full lesson script (opening hook, explanation, example, practice prompt, summary), "
                "lesson slides outline (title + 3 key points per slide), "
                "supplementary reading recommendations, "
                "worked examples (2 per lesson), "
                "common student questions and answers, "
                "and a lesson recap / key takeaways section."
            ),
            config=AgentConfig(max_tokens=5000),
        ),
        AgentSpec(
            name="Assessment Designer",
            role="Quizzes, projects, and mastery evaluation specialist",
            instructions=(
                "You are an assessment design expert. Create: "
                "module-end quiz (10 questions: multiple choice, true/false, short answer) for each of 3 modules, "
                "1 capstone project brief with rubric (4 grading criteria, 4 performance levels each), "
                "peer review protocol for the capstone, "
                "self-assessment reflection prompts, "
                "and a competency badge / certification criteria checklist. "
                "Ensure assessments measure application, not just recall."
            ),
            config=AgentConfig(max_tokens=4000),
        ),
    ],
    debate_topics=[
        "What pedagogical approach best achieves mastery for this subject?",
        "Direct instruction (clear explanation → example → practice, high efficiency)",
        "Problem-based learning (start with real challenge, derive knowledge from struggle)",
        "Flipped classroom (consume content async, apply synchronously in community)",
        "Spaced repetition with interleaving (maximize long-term retention over short-term performance)",
    ],
    expected_outputs=[
        "Full course outline with module/lesson breakdown",
        "Learning objectives using Bloom's taxonomy",
        "3 complete lesson scripts with slides outline",
        "Module-end quizzes (10 questions each)",
        "Capstone project brief with rubric",
        "Course platform recommendation",
        "Competency badge criteria",
    ],
))
