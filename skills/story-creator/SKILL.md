---
name: story-creator
description: Initialize a TennisGazelle-style stories backlog in a repository or create the next numbered story while preserving that repository's existing story schema and conventions. Use when the user asks to create a story, add the next story, initialize stories, turn planned work into a story, or establish local story/GitHub-issue workflow in a repo.
---

# Story Creator

## Goal

Provide one predictable story workflow across personal repositories while respecting local differences.

This skill has exactly two modes:

1. **Initialize** a repository that does not yet have `stories/`.
2. **Create the next story** in a repository that already has `stories/`.

It is modeled on the working conventions in **TennisGazelle/HexNets** and **TennisGazelle/piggy-bank**. **TennisGazelle/geograffiti** is an example of a personal repo that may enter through the initialization path because it does not currently use this backlog structure.

## Core invariants

These are common across the established repos and should remain stable:

- Stories live in `stories/`.
- Numbered story files use `NNN-kebab-slug.md`.
- `NNN` is local recommended sequence/order, not a GitHub issue number.
- The filename slug is stable even if the issue title changes later.
- GitHub issue linkage is stored in frontmatter as `issue` when the repo uses issue syncing.
- New local stories start without a GitHub issue; the sync workflow creates/link them.
- Story bodies use Markdown checklists for concrete acceptance criteria.
- Canonical technical/research docs should be linked, not copied wholesale into stories.
- Existing repository conventions outrank this skill's defaults.

## Mode selection

From the repository root:

```bash
test -d stories && echo existing || echo initialize
```

If `stories/` does not exist, use **Initialize**.
If it exists, use **Create next story**.

Do not create an alternative directory such as `plans/stories/`, `.stories/`, or `docs/stories/` unless the repository already establishes that as canonical and the user explicitly wants to keep it.

# Mode 1: Initialize a repository

## 1. Inspect before writing

Read at minimum:

- root `README.md`;
- `AGENTS.md`, `CLAUDE.md`, or equivalent agent docs if present;
- `Makefile` if present;
- dependency manifests (`pyproject.toml`, `requirements*.txt`, `package.json`, etc.);
- existing planning directories such as `plans/`, `roadmap/`, `issues/`, or `docs/`.

The goal is to integrate stories into the repo rather than create a disconnected island.

## 2. Create `stories/README.md`

Use the shared baseline below unless the repository clearly calls for a richer schema:

```markdown
# Story Backlog

Local story files mirror GitHub issues one-to-one. GitHub is the external collaboration surface; this directory is the agent-friendly local copy for planning, status, and acceptance criteria.

## Naming

Use `NNN-kebab-slug.md`, where `NNN` is local recommended order. Keep the filename stable even if the GitHub title changes.

## Frontmatter

- `story`: stable local story id, matching `NNN`.
- `issue`: GitHub issue number, or `null` until created.
- `status`: `planned`, `in_progress`, `blocked`, `done`, or `wont_do`.
- `title`: GitHub issue title.
- `labels`: GitHub labels to apply when syncing.
- `sync.last_remote_updated`: last GitHub update timestamp, or `null`.
- `sync.content_sha256`: script-managed body hash, or `null`.

Stable identity is the filename plus `issue`, not the title.
```

Default new-repo frontmatter:

```yaml
---
story: '001'
issue: null
status: planned
title: Example story title
labels: []
sync:
  last_remote_updated: null
  content_sha256: null
---
```

Use `status` rather than inventing phases for a fresh repo. `recommended_order` and `phase` are optional project-specific extensions, as demonstrated by HexNets, and should only be introduced when they serve an actual planning need.

## 3. Install story synchronization tooling

The initialized repo should be immediately capable of joining the established GitHub-issue workflow.

Preferred source is the sibling `story-syncer` skill:

```bash
mkdir -p scripts
cp .agents/skills/story-syncer/scripts/sync_github_stories.py scripts/sync_github_stories.py
chmod +x scripts/sync_github_stories.py
```

If invoked from a global skills installation, resolve the sibling skill's real path and copy from there.

Add the Makefile target, preserving all existing content:

```make
.PHONY: stories-sync

stories-sync:
	@python3 scripts/sync_github_stories.py sync --force remote
	@python3 scripts/sync_github_stories.py push
```

If no Makefile exists, creating a minimal Makefile containing only this target is acceptable.

The sync script requires `gh`, Python 3, and PyYAML. Add PyYAML to an existing Python development dependency manifest only when there is an obvious canonical place. Do not create a second competing dependency system merely for this script.

## 4. Integrate discoverability

Add a short link from the repo's agent/project navigation docs when those docs exist. Typical additions:

- `AGENTS.md`: backlog → `stories/README.md`.
- README contributor/development section: optional single link if stories are relevant to human contributors.

Do not dump story procedure text into multiple hubs. Keep `stories/README.md` canonical and link to it.

## 5. Create story 001 only when there is an actual story to capture

Initialization by itself does not require a fake placeholder story. If the user supplied concrete work, initialize the directory and create `001-<slug>.md` in the same change. Otherwise leave only the README/tooling.

# Mode 2: Create the next story

## 1. Read the local convention first

Inspect:

```bash
cat stories/README.md
ls stories/[0-9][0-9][0-9]-*.md | sort | tail -5
```

Read the last 2-3 numbered stories, not only the highest filename. This reveals whether fields are stable or transitional.

The local README is authoritative for schema. Existing examples are evidence, not permission to contradict an explicit README rule.

## 2. Determine the next local index

Use numbered filenames, not issue numbers and not the `story` field alone:

```text
max(NNN from stories/NNN-*.md) + 1
```

Format as three digits (`001`, `029`, `030`, ...). Do not fill old gaps unless the user explicitly asks to repair numbering. The goal is append-only local ordering.

## 3. Infer frontmatter schema

Preserve the repository's existing keys and types.

### HexNets-style example

A new story may carry:

```yaml
story: 30
recommended_order: 30
phase: 5
issue: null
title: ...
labels: [...]
status: planned
```

Do not assume the phase value purely from the new number. Infer from neighboring stories and the workstream; if phase is genuinely ambiguous, keep the prevailing phase only when that is clearly how the repo behaves, otherwise leave the field for an explicit decision.

### piggy-bank-style example

A new story should look more like:

```yaml
story: '032'
issue: null
status: planned
title: ...
labels: [...]
sync:
  last_remote_updated: null
  content_sha256: null
```

Do not add HexNets' `phase` or `recommended_order` fields to Piggy Bank merely because another repository uses them.

### Unknown schemas

For unfamiliar repos:

- preserve top-level keys used consistently by recent stories;
- reset generated/linkage fields (`issue`, `sync.*`) rather than copying old values;
- set `status` to `planned` if the schema has status;
- increment fields whose meaning is clearly local order (`story`, `recommended_order`);
- do not copy completion timestamps, implementation PRs, assignees, or other story-specific values unless the repo documents that convention.

## 4. Choose a stable filename

Slug rules:

- lowercase ASCII when practical;
- words separated by `-`;
- remove punctuation rather than encoding it;
- describe the durable capability, not transient implementation detail;
- do not include the GitHub issue number.

Example:

```text
030-add-sequential-retention-metrics.md
```

A later title rewrite should not rename the file unless there is a compelling reason.

## 5. Write a story that is implementation-ready

Match the repository's prevailing body structure. If there is no stronger convention, use:

```markdown
# <Title>

## Goal

<one concise outcome>

## Why

<why this belongs in the project now>

## Scope

- [ ] ...

## Tests

- [ ] ...

## Acceptance criteria

- [ ] ...

## Out of scope

- ...
```

For product/user-facing repositories, `## User Story` plus `## Acceptance Criteria` may be a better fit, as used by Piggy Bank. For research/infrastructure repositories, HexNets' `Goal / Why / Scope / Tests / Acceptance criteria` shape is usually more actionable.

Acceptance criteria should be observable. Prefer "CLI persists X in run metadata and a unit test verifies it" over "support X".

## 6. Link existing source-of-truth docs

Before duplicating architecture, product requirements, formulas, or research definitions into the story, locate the canonical document and link it.

A story should contain enough context to execute the work, but it should not become a fork of `SPEC.md`, architecture docs, research notes, or API documentation.

## 7. Do not create the GitHub issue directly unless asked

Normal flow:

1. Create the local story with `issue: null`.
2. Review/commit it with the codebase.
3. Run `story-syncer` / `make stories-sync` to create or update the GitHub issue.

This keeps local story numbering independent from GitHub issue numbering and lets the sync script write linkage metadata consistently.

If the user explicitly asks for immediate GitHub issue creation, it is still preferable to create the local story first and then invoke the syncer on that single file.

## Bundled helper

This skill includes `scripts/create_story.py`, which can scaffold the next story or initialize a missing `stories/` directory:

```bash
python3 .agents/skills/story-creator/scripts/create_story.py --repo-root . --title "Add sequential-task training workflow"
```

Useful options:

```bash
--labels research,testing
--phase 5
--body-style research
--init-only
--dry-run
```

The helper is intentionally conservative. It scaffolds metadata and body structure; the agent must still tailor Goal/Why/Scope/Acceptance Criteria to the actual requested work.

## Validation

After creation:

```bash
python3 - <<'PY'
from pathlib import Path
import re
files = sorted(Path('stories').glob('[0-9][0-9][0-9]-*.md'))
nums = [int(re.match(r'(\d{3})-', f.name).group(1)) for f in files]
assert len(nums) == len(set(nums)), 'duplicate story index'
print(files[-1] if files else 'stories initialized; no numbered story yet')
PY

git diff -- stories/ Makefile scripts/sync_github_stories.py
```

If the story is intended to be published immediately, run a targeted dry-run through `story-syncer` before pushing it.

## Output

Report:

- whether the repo was initialized or an existing backlog was extended;
- the new local story number and path, if created;
- which local schema was inferred;
- any tooling installed (`stories/README.md`, sync script, Makefile target);
- whether the GitHub issue is still unlinked (`issue: null`) or was synchronized separately.

## Quality bar

- Never derive local story number from GitHub issue number.
- Never renumber existing stories implicitly.
- Never overwrite repo-specific frontmatter conventions with another repo's schema.
- Never create placeholder stories just to make initialization look complete.
- Keep story bodies actionable, testable, and linked to canonical project docs.
- Prefer the smallest schema that already works for the target repository.
