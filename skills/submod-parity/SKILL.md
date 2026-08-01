---
name: submod-parity
description: >
  Sync git submodules under lib/ to the parent repo's equivalent branch tip
  (exact name match, with master↔main alias), then re-copy mapped upstream
  skill trees into skills/ and refresh CATALOG.md. Use when the user asks for
  submodule parity, to sync submodule branches, update vendored skills from
  lib/, keep subskills in check, refresh ponytail copies, or run
  submod-parity / ./scripts/submod-parity.sh.
---

# Submodule parity

Keep `lib/` submodules and their vendored copies in `skills/` aligned with the
parent branch.

## Goal

1. For each git submodule, check out the **latest tip** of the branch that
   matches the parent branch name.
2. Re-vendor mapped skill content into `skills/` (copies, not symlinks).
3. Refresh `CATALOG.md`. Do **not** commit unless the user asks.

## Workflow

Prefer the helper script (idempotent, reports clearly):

```bash
./scripts/submod-parity.sh
# optional:
./scripts/submod-parity.sh --branch develop
./scripts/submod-parity.sh --dry-run
./scripts/submod-parity.sh --no-vendor   # branch sync only
```

### Manual equivalent (if the script is unavailable)

1. **Parent branch** — `git rev-parse --abbrev-ref HEAD` (or use an explicit
   branch if HEAD is detached).
2. **Init** — `git submodule update --init --recursive` if a submodule path
   is empty.
3. **Per submodule**
   - `git -C <sub> fetch --prune origin`
   - Prefer `origin/<parent-branch>` if it exists.
   - Else if parent is `master` and `origin/main` exists (or parent `main` and
     `origin/master`), use that alias. No other aliases.
   - If neither exists: skip and report — do not invent a fallback branch.
   - `git -C <sub> checkout -B <branch> origin/<branch>`
4. **Re-vendor** (current mapping):

```text
lib/ponytail/skills/<name>/SKILL.md  →  skills/<name>/SKILL.md
lib/ponytail/docs/platform-native.md →  skills/ponytail/references/platform-native.md
```

Then run `./scripts/ponytail-vendor-adapt.sh` so Source banners, the
platform-native ladder link, and the help Update section stay correct.
5. **Catalog** — `./scripts/sync-catalog.py`
6. **Report** — parent branch, per-submodule old→new SHA / branch / skip
   reason, files refreshed. Remind the user to review and commit.

## Branch matching rules

| Parent branch | Submodule remote | Action |
|---------------|------------------|--------|
| `develop` | `origin/develop` exists | checkout that tip |
| `master` | `origin/master` missing, `origin/main` exists | use `main` (alias) |
| `main` | `origin/main` missing, `origin/master` exists | use `master` (alias) |
| any | neither exact nor alias | skip |

## Quality bar

- Exact name match first; only `master`↔`main` as alias.
- Never auto-commit submodule bumps or vendored diffs.
- Overwrite upstream-owned vendored files on each successful vendor pass;
  re-apply adaptations via `ponytail-vendor-adapt.sh`.
- Surface skips clearly (uninitialized submodule, no equivalent branch).
