---
name: create-release
description: Prepare a guarded release pull request from develop into main. Use when the user asks to create a release, open a release PR, or promote develop to main.
---

# Create Release

## Goal

Create or update a GitHub release PR from `develop` into `main` after confirming the local repo is on the latest `develop` and that merging into `main` would not conflict.

Follow the body conventions from the `/pr-body` skill. If available, read `~/.agents/skills/pr-body/SKILL.md` before drafting the PR body.

## Guarded Workflow

1. Inspect repo state:
   - Run `git status --short`.
   - Run `git branch --show-current`.
   - Run `git fetch origin main develop`.

2. Ensure the working branch is `develop`:
   - If the current branch is not `develop`, stash local changes before switching:
     - Use `git stash push -u -m "create-release: before switching to develop <YYYY-MM-DD>"` when `git status --short` is non-empty.
     - Run `git switch develop`.
   - If switching branches, stashing, or fetching fails, stop and report the blocker.

3. Refresh `develop`:
   - Run `git pull --ff-only origin develop`.
   - If the pull is blocked by local changes, non-fast-forward history, conflicts, or any other error, stop and do not proceed.

4. Check whether the release merge would conflict:
   - Use an isolated temporary worktree so the current repo is not modified:

```bash
tmpdir="$(mktemp -d)"
git worktree add --detach "$tmpdir" origin/main
(
  cd "$tmpdir" &&
  git merge --no-commit --no-ff develop
)
merge_status=$?
git worktree remove --force "$tmpdir"
test "$merge_status" -eq 0
```

   - If the merge check fails, stop and report that `develop` cannot currently merge into `main` cleanly.

5. Create or update `pr-body.md` using `/pr-body` release conventions:
   - Treat `main` as the base and `develop` as the head.
   - Inspect `git log --oneline --merges origin/main..develop`, `git log --oneline origin/main..develop`, and `git diff --stat origin/main...develop`.
   - Use `gh` to identify included PRs when possible.
   - Write `pr-body.md` at the repo root.
   - Use a high-level changelog of features and fixes going into `main`.
   - Keep the body concise, categorized, and reviewer-oriented.

6. Find an existing release PR:
   - Run `gh pr list --base main --head develop --state open --json number,url,title`.
   - If an open PR already exists, update it rather than creating a duplicate.
   - If no open PR exists, create one with `gh pr create --base main --head develop --body-file pr-body.md --title "<title>"`.

7. Title the PR:
   - If an existing PR title already contains `Release`, leave it unchanged unless the user asks otherwise.
   - Otherwise use `Release <date>: <summary>`.
   - Use local date format like `6/9/2026`.
   - Infer `<summary>` from the changelog, for example `Zip file Bug Fixes and new Run Page Functionality`.
   - If updating an existing PR whose title lacks `Release`, run `gh pr edit <number> --title "<title>" --body-file pr-body.md`.

## Stop Conditions

Stop immediately and do not open or update the release PR when:

- `git stash`, `git switch develop`, `git fetch`, or `git pull --ff-only origin develop` fails.
- The isolated merge check reports conflicts.
- GitHub CLI authentication or permissions prevent safely identifying or editing the PR.
- The repository state is ambiguous enough that proceeding could overwrite local work.

When stopping, explain the blocker and the last successful step.
