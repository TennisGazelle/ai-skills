# ai-skills

Cross-tool catalog of AI agent skills for **Cursor**, **Claude Code**, and **Codex**.

Canonical global skills live in [`skills/`](skills/) and are indexed in [`CATALOG.md`](CATALOG.md) via [`registry.yaml`](registry.yaml). Repo-local skills stay in each project's `.agents/skills/`.

## Install

There are two complementary modes — use either or both.

### Mode 1: Global (per machine)

Makes every skill available in every project on this machine.

```bash
git clone https://github.com/tennisgazelle/ai-skills.git ~/dev/ai-skills
cd ~/dev/ai-skills
./scripts/bootstrap.sh
```

`bootstrap.sh` creates symlinks:

| Symlink | Target | Used by |
|---------|--------|---------|
| `~/.agents/skills` | `<clone>/skills` | Cursor, Codex |
| `~/.claude/skills` | `<clone>/skills` | Claude Code |
| `~/.cursor/skills` | `<clone>/skills` | Cursor (older layouts) |

Restart Cursor / Claude Code / Codex after bootstrap so new skills are picked up.

### Mode 2: Per-repo (git submodule)

Pins the skills to a version inside a consuming repo, so the catalog travels with the codebase and collaborators get it via git.

```bash
# from the consuming repo root
git submodule add https://github.com/tennisgazelle/ai-skills.git .agents/ai-skills
./.agents/ai-skills/scripts/install-into-repo.sh
git add .agents .claude .gitmodules
git commit -m "Add ai-skills submodule"
```

`install-into-repo.sh` creates one relative symlink per global skill (`.agents/skills/<name> -> ../ai-skills/skills/<name>`) plus `.claude/skills -> ../.agents/skills`, so repo-local skills coexist in the same directory. Re-run it after updating the submodule; it prunes links for removed skills and never touches real (repo-local) skill directories.

Collaborators clone with `git clone --recurse-submodules` (or run `git submodule update --init` after a plain clone). Commit the symlinks — git stores them natively; Windows users need symlink support enabled (`git config core.symlinks true` + Developer Mode).

To update a consuming repo to the latest skills:

```bash
git submodule update --remote .agents/ai-skills
./.agents/ai-skills/scripts/install-into-repo.sh
```

## Where skills live

```text
ai-skills/                          # this repo (global skills)
  skills/<name>/SKILL.md

<repo>/.agents/skills/<name>/       # repo-local (committed to that repo)
<repo>/.agents/ai-skills/           # optional submodule mount (mode 2)
<repo>/.claude/skills -> .agents/skills   # Claude Code symlink
```

Cursor and Codex read `.agents/skills/` natively. Claude Code reads `.claude/skills/` only — hence the symlink.

## Decision rubric: global vs repo-local

| Keep **repo-local** when… | Promote to **global** when… |
|---------------------------|----------------------------|
| Skill hardcodes repo paths, stack names, or conventions | Skill is a generic workflow with no repo-specific assumptions |
| Skill only makes sense for one codebase | You used it successfully, unmodified, in a **second** repo (rule of two) |
| Team should own the skill with the repo | You want it on every machine and in every project |

**When unsure, start repo-local.** Use `./scripts/promote.sh <repo> <skill>` after the rule-of-two check.

## Catalog maintenance

- **Global skills:** edit `skills/<name>/SKILL.md`; run `./scripts/sync-catalog.py` to refresh `CATALOG.md`.
- **Repo-local skills (machine-specific):** copy `registry.local.yaml.example` to `registry.local.yaml` (gitignored), add your repo paths, then run `./scripts/sync-catalog.py` — repo-local rows land in `CATALOG.local.md` (also gitignored), keeping the committed catalog clean.
- **Promote / demote:** `./scripts/promote.sh` and `./scripts/demote.sh` move skills between a repo and the global catalog.

## Related docs

- [CATALOG.md](CATALOG.md) — human-readable index of global skills
- [registry.yaml](registry.yaml) — machine-readable index
- [registry.local.yaml.example](registry.local.yaml.example) — template for the machine-specific overlay
