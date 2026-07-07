---
name: test-coverage-gap
description: Find untested or under-tested code and propose targeted unit tests including edge cases. Use when the user asks to improve code coverage, add tests to files missing them, find test gaps, or verify formulas/behavior with perfect-fit, poor-fit, and edge-case scenarios.
---

# Test Coverage Gap

## Goal

Identify high-value test gaps and propose concrete tests — not a blanket "add more tests" sweep.

## Workflow

1. **Discover test tooling**
   - Look for `pytest`, `jest`/`vitest`, `coverage.py`, `Makefile` targets (`test`, `coverage`, `lint-check`).
   - Prefer existing project commands over inventing new ones.

2. **Run coverage when available**

```bash
# Python (common patterns — pick what the repo uses)
python -m pytest --cov=<package> --cov-report=term-missing
# or
make test-coverage
```

   - If coverage cannot run (missing deps, no config), fall back to: list source files vs test files and diff by module path.

3. **Rank gaps by risk**
   Prioritize files/modules that are:
   - Recently changed (`git log --name-only -10`)
   - High complexity (many branches, public API surface)
   - Previously buggy or mentioned in user context
   - Zero or near-zero coverage

4. **Propose tests with edge cases**
   For each proposed test file/function, specify:
   - **Happy path** — normal expected input/output
   - **Edge cases** — empty input, boundary values, low-sample / single-row data
   - **Failure modes** — invalid input, permission errors, missing files
   - **Regression** — the specific bug or formula the user asked to verify

   Match the user's style when they ask for formula verification (e.g. "perfect fit, poor fit, low-sample").

5. **Output format**

```markdown
## Coverage Gap Report — <repo>

### Commands run
- ...

### Top gaps (ranked)
| Priority | File | Coverage | Why it matters |
|----------|------|----------|----------------|
| 1 | ... | ...% | ... |

### Proposed tests
#### <module/path>
- `test_<name>`: <what it asserts> — cases: happy, edge, failure

### Out of scope (and why)
- ...
```

6. **Implement only when asked**
   - Default: report + proposals.
   - If user says "add the tests", implement highest-priority gaps first and run the narrowest relevant test command.

## Quality bar

- Do not claim coverage numbers without running tooling or stating estimates.
- Prefer one focused test per behavior over large fixture-heavy suites unless the repo already uses that pattern.
