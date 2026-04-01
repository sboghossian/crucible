# Contributing to Crucible

Crucible is an early-stage research project. The best contributions right now are the ones that stress-test the core design, not the ones that extend it.

---

## What We're Looking For

**High value:**
- Real-world debate transcripts that produced surprising or wrong results — these are bugs in the design
- Persona refinement: if a persona's arguments are consistently unconvincing, that's a calibration problem
- Edge cases in the orchestration pipeline that produce incorrect or inconsistent output
- Documentation that reflects actual behavior (not aspirational behavior)
- New agent implementations with a clear use case (open an issue first)

**Lower priority right now:**
- UI improvements (we need the core to be right before we polish)
- Performance optimizations (correctness before speed)
- New configuration options (don't add them unless someone actually needs them)

---

## Getting Started

```bash
# Fork and clone
git clone https://github.com/your-username/crucible
cd crucible

# Install in dev mode
pip install -e ".[dev]"

# Run the test suite
pytest tests/ -v

# Run a specific test file
pytest tests/test_debate_council.py -v
```

**Requirements:** Python 3.11+, Anthropic API key (`ANTHROPIC_API_KEY` environment variable)

Some tests make real API calls (marked with `@pytest.mark.api`). These cost real money. Run them intentionally:

```bash
pytest tests/ -m "not api"     # skip API tests
pytest tests/ -m api           # only API tests
```

---

## Development Workflow

1. **Open an issue first** for anything non-trivial. A quick discussion before you build saves everyone time.
2. Branch from `master`: `feat/your-description` or `fix/your-description`
3. Write tests before marking complete. If you're fixing a bug, the test should fail before your fix and pass after.
4. Run the full test suite locally before opening a PR.
5. Keep commits atomic and use conventional commit format: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`

---

## Pull Request Standards

- **One thing per PR.** Split unrelated changes.
- **Tests included.** PRs without tests for new behavior will be asked to add them.
- **Changelog entry.** If it affects behavior, add a line to `CHANGELOG.md`.
- **No scope creep.** Fix what you said you'd fix; don't refactor surrounding code unless it's directly necessary.

### PR Description Template

```
## What this does
One sentence.

## Why
One sentence — link to an issue if there is one.

## How to test it
Specific commands or steps.

## Edge cases considered
What could go wrong? Did you test it?
```

---

## Persona Contributions

The four Debate Council personas are the most important part of Crucible. If you want to contribute persona improvements:

1. Document the current behavior: what arguments does the persona make? How does it score?
2. Describe the gap: where is it failing? (Wrong weights? Missing considerations? Poorly calibrated cross-examination?)
3. Propose a specific change to the persona's system prompt or scoring weights
4. Provide before/after debate transcripts showing the improvement

Persona changes affect every debate. They require careful review.

---

## Reporting Bugs

Use the [bug report template](.github/ISSUE_TEMPLATE/bug_report.md). Include:
- The full input (topic, options, context) that triggered the bug
- The actual output
- What you expected instead
- Your Python version and Crucible version

Debate quality issues (the persona argued badly, the wrong option won) are especially valuable. Include the full transcript.

---

## Code Style

- Python 3.11+, typed with strict mypy
- `ruff` for linting, `black` for formatting (run `ruff check .` and `black .` before committing)
- No `print()` in library code — use the logger
- No `Any` in type annotations
- Docstrings on public APIs only; not on every function

---

## Questions?

Open a Discussion, not an issue. Issues are for bugs and concrete feature requests. Discussions are for questions, ideas, and exploration.
