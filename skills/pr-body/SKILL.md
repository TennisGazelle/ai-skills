---
name: pr-body
description: Generate or replace a repo-root pr-body.md from the current branch diff, with concise categorized bullets, and update an existing GitHub PR body via REST API (never gh pr edit — GraphQL Projects classic is broken). Use when the user asks for a PR body, PR summary, branch summary, or copy-pastable pull request description.
disable-model-invocation: true
---

# PR Body

## Goal

Create or replace `pr-body.md` at the repository root with a super concise, categorized, bullet-pointed summary of what the current branch changes relative to its base. The file should be ready to paste into a GitHub PR body.

If the current branch already has a GitHub PR, update that PR body from `pr-body.md`. If no PR exists, only create the file.

## Protected Branch Guard

Before doing anything else:

1. Run `git branch --show-current`.
2. If the branch is `develop`, `main`, or `master`, stop and tell the user the current branch is protected.
3. Exception: if the user explicitly says `this is develop being merged into main`, continue with the release workflow below.

Do not create or update `pr-body.md` on a protected branch unless the release exception applies.

## Standard Workflow

1. Inspect repository and PR state:
   - Run `git status --short`.
   - Run `git branch --show-current`.
   - Run `gh pr view --json number,url,baseRefName,headRefName,title` to identify an existing PR for the current branch. If there is no PR, continue without updating GitHub.

2. Determine the base branch:
   - Prefer the existing PR's `baseRefName`.
   - Otherwise use the repository default branch from `gh repo view --json defaultBranchRef`.
   - If needed, fall back to `develop`, then `main`, then ask the user.

3. Inspect the branch diff:
   - Run `git fetch origin <base>` when a remote base exists.
   - Run `git log --oneline <base>..HEAD`.
   - Run `git diff --stat <base>...HEAD`.
   - Run `git diff <base>...HEAD`.
   - Do not include unrelated uncommitted local changes unless the user explicitly asks. Mention separately if relevant.

4. Write `pr-body.md` at the repo root:
   - Replace the file if it already exists.
   - Keep the body concise and useful for reviewers.
   - Use categorized bullets.
   - Focus on user-facing behavior, operational impact, tests, docs, and risk.
   - Avoid file-by-file summaries unless the PR is mostly docs or CI.
   - Do not claim tests passed unless they were run or the user supplied results.

5. Update GitHub only when a PR already exists:
   - **Do not use `gh pr edit`** for the body — it goes through GraphQL and fails on deprecated Projects (classic) fields.
   - Resolve the repo once: `gh repo view --json nameWithOwner -q .nameWithOwner` (e.g. `owner/repo`).
   - PATCH the PR body via REST:
     ```bash
     gh api "repos/${OWNER_REPO}/pulls/${PR_NUMBER}" -X PATCH -f body="$(cat pr-body.md)"
     ```
   - Do not create a new PR unless the user explicitly asks.

## Body Format

Use this default format, omitting empty sections:

```markdown
## Summary
- **Category:** concise change summary.
- **Category:** concise change summary.

## Verification
- Passed: ...
- Not run: ...
```

Good categories include:
- **CLI**
- **Web**
- **Database**
- **CI**
- **Docs**
- **Tests**
- **Release**
- **Fixes**

Prefer 3-7 total bullets across the body.

## Release Workflow

Use this only when the user explicitly says `this is develop being merged into main`.

1. Treat `main` as the base and `develop` as the head.
2. Inspect `git log --oneline --merges main..develop`, `git log --oneline main..develop`, and `git diff --stat main...develop`.
3. Use `gh` to identify merged PRs included in `develop` and not yet in `main` when possible.
4. Write `pr-body.md` categorized by PRs first, then a brief changelog.
5. Keep it concise: PR number/title plus one short bullet per meaningful change.

Release body format:

```markdown
## Included PRs
- #123: PR title — short impact.
- #124: PR title — short impact.

## Changelog
- **Category:** concise release note.
- **Category:** concise release note.

## Verification
- ...
```
