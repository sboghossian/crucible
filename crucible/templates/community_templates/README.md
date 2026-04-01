# Community Templates

This directory contains community-submitted agent templates for Crucible.

## Structure

```
community_templates/
├── README.md              ← You are here
├── TEMPLATE.md            ← Template for submitting a new template (meta!)
├── example_submission/    ← A complete example community template
│   └── __init__.py
└── installed/             ← Templates installed via `crucible templates install`
```

## Submitting a Template

1. Copy `TEMPLATE.md` and follow the structure guide.
2. Create a directory (e.g. `my_template/`) with an `__init__.py` that defines:
   - `SUBMISSION` — a `TemplateSubmission` instance with your author info
   - `TEMPLATE` — a `Template` instance registered via `template(...)`
3. Validate locally: `crucible templates validate ./my_template`
4. Open a pull request against the `main` branch of the Crucible repository.

## Quality Gates

Your template must pass all of the following before it can be merged:

- [ ] `SUBMISSION.author` is non-empty
- [ ] `SUBMISSION.description` is non-empty
- [ ] At least **2 agents** defined
- [ ] At least **1 debate topic** defined
- [ ] At least **1 expected output** defined
- [ ] Template description is present and meaningful

## Installing a Community Template

```bash
# Install from a local directory
crucible templates install ./path/to/my_template

# Install from a .py file
crucible templates install ./my_template.py
```

## Listing Community Templates

```bash
crucible templates --community
```

## Validating Before Submission

```bash
crucible templates validate ./my_template
```
