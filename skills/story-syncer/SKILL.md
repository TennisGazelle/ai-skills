---
name: story-syncer
description: Synchronize a repository's numbered stories/*.md backlog with GitHub issues using the TennisGazelle story conventions. Use when the user asks to sync stories, reconcile story files with GitHub issues, run the stories-sync workflow, pull issue progress into local stories, or push new/updated stories to GitHub.
---

# Story Syncer

## Goal

Keep the repository-local `stories/NNN-kebab-slug.md` backlog and GitHub issues aligned without changing the repository's own story schema.

This skill codifies the workflow already used by repositories such as **TennisGazelle/HexNets** and **TennisGazelle/piggy-bank**. In both repositories, local Markdown is the agent-friendly planning copy and GitHub issues are the external collaboration surface. The stable identity is the numbered filename plus the `issue` field, not the mutable issue title.

The normal full sync is intentionally equivalent to the existing `make stories-sync` targets:

```bash
python3 scripts/sync_github_stories.py sync --force remote
python3 scripts/sync_github_stories.py push
```

That means **GitHub wins first for already-linked stories**, then local stories without issues and any remaining local metadata/body differences are pushed.

## Repository conventions to preserve

Do not normalize every repo to one frontmatter schema.

Known examples:

- **HexNets** uses numbered filenames plus fields such as `story`, `recommended_order`, `phase`, `title`, `labels`, optional `status`, `issue`, and `sync` metadata. Its local ordering number is not the GitHub issue number.
- **piggy-bank** uses numbered filenames plus `story`, `issue`, `status`, `title`, `labels`, and `sync`. Its README explicitly says not to add `recommended_order` or `phase` unless the repo later adopts them.
- Other personal repos may not have `stories/` yet. Do not initialize them here; route that to the `story-creator` skill.

The sync implementation must preserve unknown frontmatter keys verbatim. It may update only fields it owns: `issue`, `title`, `labels`, and `sync.*`.

## Preconditions

From the target repository root, verify:

```bash
git rev-parse --show-toplevel
gh auth status
```

Required:

- `gh` installed and authenticated for the target repository.
- Python 3.
- PyYAML (`python3 -c 'import yaml'`).
- A `stories/` directory containing `NNN-*.md` files.

If `stories/` is missing, stop this workflow and use `story-creator` to initialize it.

## Choose the implementation

Use the repo's own tooling when it exists. This keeps behavior pinned with the project.

1. If `make stories-sync` exists, prefer it.
2. Else if `scripts/sync_github_stories.py` exists, run the two commands directly.
3. Else use this skill's bundled script against the current repo:

```bash
python3 .agents/skills/story-syncer/scripts/sync_github_stories.py --repo-root . sync --force remote
python3 .agents/skills/story-syncer/scripts/sync_github_stories.py --repo-root . push
```

For a global installation rather than a repo submodule, resolve the installed skill path and invoke the same bundled script with `--repo-root <target-repo>`.

Do not silently replace a repo-local sync script merely because the bundled copy is newer. Repo-local behavior is part of that repository's contract. If the user asks to upgrade the tooling, compare the scripts and make that a separate explicit change.

## Full sync workflow

### 1. Inspect local state

```bash
git status --short -- stories scripts/sync_github_stories.py Makefile
```

The canonical `stories-sync` behavior is remote-first and can overwrite local story-body edits on already-linked stories. If story files are dirty, surface that fact before running the destructive remote-first step. When the user explicitly asked for the canonical full sync, continue after clearly identifying the files at risk; otherwise prefer a dry run or targeted sync.

### 2. Dry-run when state is ambiguous

```bash
python3 scripts/sync_github_stories.py sync --dry-run
```

Useful targeted forms:

```bash
python3 scripts/sync_github_stories.py sync --only stories/015-add-sequential-task-training-workflow.md --dry-run
python3 scripts/sync_github_stories.py sync --issue 34 --dry-run
```

### 3. Pull remote state first

```bash
python3 scripts/sync_github_stories.py sync --force remote
```

For every story with `issue: N`, this updates local body/title/labels from GitHub and records synchronization metadata. Local-only stories with `issue: null` are skipped during this phase.

### 4. Push local/new stories

```bash
python3 scripts/sync_github_stories.py push
```

This must:

- create a GitHub issue for a story whose `issue` is null;
- write the new issue number back into frontmatter;
- create missing GitHub labels when possible;
- update issue title/body/labels when local differs;
- preserve repo-specific frontmatter fields;
- update `sync.last_remote_updated` and `sync.content_sha256` when those fields are present or when the script owns the sync block.

### 5. Review the mutation

```bash
git diff -- stories/
git status --short
```

A sync may legitimately change frontmatter even when the Markdown body did not change, especially after creating issues or refreshing timestamps/hashes.

## Targeted operations

Use these instead of full remote-first synchronization when the user is precise about direction.

Pull one story from GitHub:

```bash
python3 scripts/sync_github_stories.py pull --only stories/NNN-slug.md
```

Push one story to GitHub:

```bash
python3 scripts/sync_github_stories.py push --only stories/NNN-slug.md
```

Sync by issue number:

```bash
python3 scripts/sync_github_stories.py sync --issue 34
```

Force local to win:

```bash
python3 scripts/sync_github_stories.py sync --force local
```

Force GitHub to win:

```bash
python3 scripts/sync_github_stories.py sync --force remote
```

## Conflict policy

Without `--force`, the script uses a conservative merge heuristic based on:

1. completed checkbox count;
2. total checklist size;
3. exact normalized body equality;
4. last known remote update timestamp.

If neither side is safely preferred, report a conflict and require an explicit direction. Never resolve ambiguous prose differences by guessing.

## GitHub labels

Missing labels should be created with a neutral default color (`ededed`) before issue creation/editing. If label creation fails, print the failing `gh` command and actionable diagnostics instead of silently dropping labels.

## Failure diagnostics

When `gh` fails, preserve and show:

- the exact `gh` command;
- exit code;
- stdout/stderr;
- targeted hints for network/DNS, auth, permissions/SSO, repository selection, labels, or rate limits.

Do not misdiagnose a transport failure as an authentication failure. In particular, `dial tcp`, DNS failures, TLS failures, or `network is unreachable` should point to connectivity first.

## Installing the tooling into a repo

Only do this when the user explicitly asks to initialize/upgrade story tooling, or when `story-creator` is initializing a repo.

Copy the bundled script:

```bash
mkdir -p scripts
cp .agents/skills/story-syncer/scripts/sync_github_stories.py scripts/sync_github_stories.py
chmod +x scripts/sync_github_stories.py
```

Add this Makefile target without disturbing existing targets:

```make
.PHONY: stories-sync

stories-sync:
	@python3 scripts/sync_github_stories.py sync --force remote
	@python3 scripts/sync_github_stories.py push
```

Do not add CI automation automatically. Automatic post-merge synchronization has repository permission and commit-loop implications and should be a separate story/decision.

## Output

After a sync, report:

- stories pulled from GitHub;
- stories pushed to GitHub;
- newly created issue numbers;
- conflicts or skipped local-only stories;
- files changed locally and whether those changes need committing.

## Quality bar

- Preserve each repository's frontmatter schema.
- Never confuse local story index with GitHub issue number.
- Never renumber existing stories during sync.
- Prefer repo-local tooling over the skill-bundled fallback.
- Make remote-first overwrite semantics explicit.
- Keep issue/body synchronization mechanical; do not rewrite story prose during a sync operation.
