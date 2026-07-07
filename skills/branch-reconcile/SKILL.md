---
name: branch-reconcile
description: Compare two git branches and produce a reconciliation plan that filters out changes already merged upstream. Use when the user asks to compare branches, reconcile long-lived branches, audit branch diffs, or avoid counting changes already included by other PRs.
---

# Branch Reconcile

## Goal

Compare two branches and produce a **clean reconciliation plan** — not a noisy raw diff that includes work already on the base.

## Inputs

Required (ask if missing):
- **Base branch** — target to merge into (e.g. `main`, `develop`)
- **Head branch** — feature branch (e.g. `feat/foo`)

Optional:
- **Upstream ref** — e.g. `origin/develop` when local base may be stale

## Workflow

1. **Refresh refs**

```bash
git fetch origin <base> <head>
```

2. **Establish merge bases**

```bash
git merge-base origin/<base> origin/<head>
git log --oneline origin/<base>..origin/<head>
git diff --stat origin/<base>...origin/<head>
```

3. **Filter "already upstream" noise**
   When the user says changes are "already included by other PRs":
   - List commits on head not in base: `git log --oneline origin/<base>..origin/<head>`
   - For each merge commit or PR merge, check if equivalent changes exist on base via `git log origin/<base> --grep=<pr-number>` or cherry-pick equivalence:
     ```bash
     git cherry -v origin/<base> origin/<head>
     ```
   - Mark commits with `-` in `git cherry` as already upstream; focus the plan on `+` commits.

4. **Categorize remaining diff**
   Group by intent, not file:
   - Features
   - Bug fixes
   - Refactors
   - Tests / CI
   - Docs
   - Conflicts / overlap with other in-flight work

5. **Conflict preview**

```bash
tmpdir=$(mktemp -d)
git worktree add --detach "$tmpdir" origin/<base>
( cd "$tmpdir" && git merge --no-commit --no-ff origin/<head> ); echo $?
git worktree remove --force "$tmpdir"
```

6. **Output format**

```markdown
## Branch Reconcile — <head> → <base>

### Summary
- Commits on head not in base: N (M already upstream)
- Files changed (unique): ...
- Merge conflicts if merged now: yes/no

### Already upstream (safe to ignore in plan)
- <sha> <subject> — reason

### Unique work on <head> (needs reconciliation)
| Area | Commits / files | Action |
|------|-----------------|--------|
| ... | ... | merge / rebase / split PR |

### Recommended plan
1. ...
2. ...

### Risks
- ...
```

7. **Do not merge or rebase** unless the user explicitly asks. Default deliverable is the plan.

## Quality bar

- Always compare against remote refs (`origin/...`) when they exist.
- Call out when head is behind base and needs a rebase/merge from base first.
