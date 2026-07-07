---
name: make-pr-body
description: Create concise GitHub pull request bodies from a head branch and base branch comparison. Use when the user asks to draft, write, generate, or prepare a PR body, or when the user asks to make a PR and wants the body prepared from branch changes.
---

# Make PR Body

## Purpose

Given a head branch and base branch, create a thorough but concise pull request body at `temp/pr-body.md`.

Use this skill when the user asks to draft or generate a PR body. If the user asks to create a PR, write the body to `temp/pr-body.md` first, then use that file as the PR body. Do not create a PR unless the user explicitly asks for it.

## Inputs

Required:
- Base branch, for example `main`
- Head branch, for example `feature/some-feature`

If either branch is missing, ask the user for it before drafting.

## Workflow

1. Inspect the branch comparison:
   - Run `git status --short` to identify unrelated local changes.
   - Run `git log --oneline <base>..<head>` to understand included commits.
   - Run `git diff --stat <base>...<head>` for scope.
   - Run `git diff <base>...<head>` to identify user-facing behavior, API changes, docs, tests, and risk.

2. Draft `temp/pr-body.md`:
   - Create `temp/` if needed.
   - Keep the body concise but specific.
   - Describe meaningful behavior and intent, not every touched file.
   - Include details as bullet points.
   - Mention tests or verification if available from context or commands the user asked you to run.
   - Avoid claiming tests passed unless you ran them or the user provided the result.

3. Use this template:

```markdown
## Overview

<!-- Optional: add broader context, motivation, or product summary before opening the PR. -->

## Changes

- ...
- ...

## Details

- ...
- ...

## Verification

- Not run (not requested).
```

Prefer 2-5 bullets under `Changes` and 2-6 bullets under `Details`. Omit empty sections only if they add no value, but keep `Overview` as the user-editable area.

## Creating a PR

Only create a PR when the user explicitly asks for one.

When creating the PR:

1. Ensure `temp/pr-body.md` has been written for the requested base/head comparison.
2. Push the head branch if needed.
3. Run:

```bash
gh pr create --base <base> --head <head> --body-file temp/pr-body.md --title "<title>"
```

If the title is not provided, infer a short title from the branch changes and confirm only when the choice is ambiguous.

## Quality Bar

- The body should be understandable to a reviewer who has not followed the branch.
- The body should be shorter than a changelog and more useful than a commit list.
- The body should separate high-level changes from implementation details.
- The body should leave room for the user to add broader motivation in `Overview`.
