# ai-skills

Cross-tool catalog of personal AI agent skills for **Cursor**, **Claude Code**, and **Codex**.

Canonical global skills live in [`skills/`](skills/). Repo-local skills stay in each project's `.agents/skills/` and are indexed in [`CATALOG.md`](CATALOG.md) via [`registry.yaml`](registry.yaml).

## Quick start

```bash
git clone git@github.com:tennisgazelle/ai-skills.git ~/dev/ai-skills
cd ~/dev/ai-skills
./scripts/bootstrap.sh
```

`bootstrap.sh` creates two symlinks:

| Symlink | Target | Used by |
|---------|--------|---------|
| `~/.agents/skills` | `~/dev/ai-skills/skills` | Cursor, Codex |
| `~/.claude/skills` | `~/dev/ai-skills/skills` | Claude Code |

Restart Cursor / Claude Code / Codex after bootstrap so new skills are picked up.

## Where skills live

```text
ai-skills/                          # this repo (global skills)
  skills/<name>/SKILL.md

<repo>/.agents/skills/<name>/       # repo-local (committed to git)
<repo>/.claude/skills -> .agents/skills   # optional Claude Code symlink
```

Cursor and Codex read `.agents/skills/` natively. Claude Code reads `.claude/skills/` only — use the symlink pattern above for repo-local skills (see [phoenix](https://github.com/Arize-ai/phoenix) for a working example).

## Decision rubric: global vs repo-local

| Keep **repo-local** when… | Promote to **global** when… |
|---------------------------|----------------------------|
| Skill hardcodes repo paths, stack names, or conventions (e.g. arbor hub-and-spoke `.claude/*.md`, benchmarking-iac stack docs) | Skill is a generic workflow with no repo-specific assumptions |
| Skill only makes sense for one codebase | You used it successfully, unmodified, in a **second** repo (rule of two) |
| Team should own the skill with the repo | You want it on every machine and in every project |

**When unsure, start repo-local.** Use `./scripts/promote.sh <repo> <skill>` after the rule-of-two check.

## Catalog maintenance

- **Global skills:** edit `skills/<name>/SKILL.md`; run `./scripts/sync-catalog.py` to refresh `CATALOG.md`.
- **Repo-local skills:** add the repo path to `registry.yaml`, then run `./scripts/sync-catalog.py`.
- **Promote / demote:** `./scripts/promote.sh` and `./scripts/demote.sh` move skills and update the registry.

See [CATALOG.md](CATALOG.md) for the full index.

## Related docs

- [CATALOG.md](CATALOG.md) — human-readable skill index
- [registry.yaml](registry.yaml) — machine-readable index and repo scan paths
