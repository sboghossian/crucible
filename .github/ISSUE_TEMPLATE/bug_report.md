---
name: Bug report
about: Something isn't working as expected
title: "[bug] "
labels: bug
assignees: ''
---

## What happened

Describe the bug clearly. If a debate produced wrong output, include the full transcript.

## To reproduce

**Full input:**
```python
# Paste the code you ran
```

**Full output:**
```
# Paste what actually happened
```

**What you expected:**
What should have happened instead?

## Environment

- Crucible version: (run `python -c "import crucible; print(crucible.__version__)"`)
- Python version: (run `python --version`)
- OS:

## Debate quality issues

If this is a debate quality issue (wrong winner, weak arguments, bad scoring), please include:

1. The full debate transcript from your output directory
2. Which round(s) produced the problematic output
3. What specifically was wrong (wrong persona won, key argument was ignored, scoring seemed miscalibrated)

Debate quality feedback is especially valuable for improving the personas.

## Additional context

Anything else relevant: error messages, relevant config, unusual inputs.
