# Template Submission Guide

Use this file as a reference when creating a new community template.

## File Structure

Create a directory named after your template (snake_case):

```
my_template_name/
└── __init__.py
```

## __init__.py Structure

```python
"""One-line description of your template — Category."""

from crucible.templates.base import AgentSpec, Template, template
from crucible.templates.community import TemplateSubmission
from crucible.core.agent import AgentConfig

# Required: submission metadata
SUBMISSION = TemplateSubmission(
    name="my_template_name",
    author="Your Name <you@example.com>",
    description="A concise, honest description of what this template does.",
    version="1.0.0",
    license="MIT",                          # or Apache-2.0, CC0-1.0, etc.
    tags=["tag1", "tag2"],
    tested_with_crucible_version="1.0.0",  # crucible version you tested with
)

# Required: the template itself
TEMPLATE = template(Template(
    name="my_template_name",               # must match SUBMISSION.name
    description="Same description as above.",
    category="Category Name",              # pick an existing category or create one
    tags=["tag1", "tag2"],
    version="1.0.0",                       # must match SUBMISSION.version
    author="Your Name",
    license="MIT",
    agents=[
        AgentSpec(
            name="Agent One",
            role="What this agent specializes in",
            instructions=(
                "Detailed instructions for the agent. Be specific about what "
                "it should produce and in what format. The more precise, the "
                "better the output quality."
            ),
            config=AgentConfig(max_tokens=2048),
        ),
        AgentSpec(
            name="Agent Two",
            role="Second specialization",
            instructions="...",
            config=AgentConfig(max_tokens=2048),
        ),
        # Add at least 2 agents
    ],
    debate_topics=[
        "The main question the debate council should resolve",
        "Option A",
        "Option B",
        "Option C",
    ],
    expected_outputs=[
        "First concrete deliverable",
        "Second concrete deliverable",
        "Third concrete deliverable",
    ],
))
```

## Checklist Before Submitting

- [ ] `SUBMISSION` and `TEMPLATE` both defined at module level
- [ ] `name` matches in both `SUBMISSION` and `TEMPLATE`
- [ ] `version` matches in both `SUBMISSION` and `TEMPLATE`
- [ ] At least 2 agents
- [ ] At least 1 debate topic
- [ ] At least 1 expected output
- [ ] `crucible templates validate ./my_template_name` passes
- [ ] Tested end-to-end with `crucible deploy my_template_name --plan`

## Naming Conventions

- Template names: `snake_case`, lowercase only, no spaces
- Agent names: Title Case, descriptive (e.g. "Market Analyst", "Content Writer")
- Category: choose from existing categories where possible
- Tags: lowercase, space-separated compound terms are fine (e.g. "machine learning")
