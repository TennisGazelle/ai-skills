---
name: doc-audit
description: Audit documentation for staleness, broken links, hub-and-spoke violations, agent entry-point coverage (CLAUDE.md/AGENTS.md/etc.), centralized rules, and change-making actionability against recent code changes. Use when the user asks for a documentation audit, doc drift check, link-first refresh, AI-context audit, or wants to verify README and spoke docs still match the codebase.
---

# Documentation Audit

## Goal

Produce a **remediation todo list** — not blind edits. Verify first, then recommend fixes.

## Workflow

1. **Map the doc layout**
   - Find hub docs: `README.md`, `AGENTS.md`, `CLAUDE.md`, `.claude/README.md` or `HUB.md`,
     or a centralized folder such as `docs/ai/README.md`.
   - Find spoke docs: `.claude/*.md`, `.cursor/*.md`, `.cursor/rules/*`, `docs/`.
   - Note hub-and-spoke rules if present (e.g. "README is navigation only; details live in spokes").

2. **Entry-point audit (discoverability by agent harness)**
   - Every harness the team uses should have a root entry stub pointing at the
     same central hub: `CLAUDE.md` (Claude Code), `AGENTS.md` (Codex and the
     cross-tool standard), `GEMINI.md` (Gemini CLI),
     `.github/copilot-instructions.md` (Copilot).
   - Flag missing stubs, stubs pointing at different docs, and fat stubs that
     carry their own divergent content instead of linking to the hub
     (duplicated rules drift apart — keep stubs thin, DRY).
   - Flag a hub with no **task router**: a table mapping "your task touches X →
     read spoke Y → code lives in Z", so agents load only the spoke they need.

3. **Identify recent code changes**
   - Run `git log --oneline -20` and `git diff --stat HEAD~20..HEAD` (adjust depth if user specifies a range or branch).
   - List modules, CLI flags, env vars, API routes, or CI steps that changed.

4. **Cross-check docs vs code**
   For each changed area, check whether spokes mention it:
   - CLI subcommands/options → `.claude/CLI.md` or equivalent
   - Env vars → `.claude/ENV.md` / `.env.example`
   - Web routes → `.claude/WEB.md`
   - CI/deploy → `.claude/CICD.md`
   - Architecture moves → `.claude/ARCHITECTURE.md`

5. **Actionability audit (minimal-token change-making)**
   The test: given a specific ask, could an agent read the hub + **one** spoke
   and know where to edit and how to fit in? Flag spokes that fail it:
   - No **file map** — a table of "file → role → change here when…" for the
     component the spoke covers.
   - Prose mentions of files/paths with no clickable relative links into the
     actual source.
   - No **style notes** — the local idioms (naming, error handling, layering,
     "don't fetch from components"-type constraints) an agent needs to make a
     change that matches the existing code.

6. **Rules audit (centralized standards)**
   - A single central rules doc (e.g. `docs/ai/rules.md`) should exist, be
     linked from every entry stub, and cover at minimum:
     - DRY: one source of truth per fact/behavior, in code and in docs.
     - Architecture best practices as applied in *this* repo: OOP where state
       lives, layering, CRUD/API conventions, matching surrounding style.
     - No-assumptions policy: verify every fact against the code or official
       docs before using it; when a decision is ambiguous, **ask the user**
       during planning instead of guessing.
     - Model policy: plan/design/review on a high-capability, high-reasoning
       model; execute the approved plan on a lower-capacity model at moderate
       reasoning effort (or emulate with an explicit plan phase + sign-off).
     - Docs updated in the same PR as the code they describe.
   - Flag a missing rules doc, missing rule areas, or rules duplicated across
     stubs/spokes instead of centralized.

7. **Link audit**
   - Scan markdown for `[text](path)` and `` [`path`](path) `` links.
   - Flag broken relative links (target file missing).
   - Flag hub docs that duplicate long spoke content instead of linking.
   - Flag spokes with no back-link to hub where the project expects bidirectional links.
   - Flag orphan spokes (no inbound link from the hub/task router) and missing
     cross-links between related spokes — the docs should be interconnected
     wikipedia-style so discovery works from any starting point.

8. **Output format**

```markdown
## Documentation Audit — <repo> — <date>

### Verified OK
- ...

### Stale (code changed, docs not updated)
- [ ] <file>: <what is wrong> — suggested fix

### Broken links
- [ ] <file>: `<link>` → missing target

### Hub/spoke violations
- [ ] <file>: duplicates content from <spoke>; should link instead

### Entry-point / router gaps
- [ ] <harness>: missing or divergent entry stub — suggested fix
- [ ] hub: task-router row missing for <component>

### Rules gaps
- [ ] rules doc: missing <rule area> (DRY / architecture / no-assumptions / model policy)

### Actionability gaps
- [ ] <spoke>: no file map / source links / style notes for <component>

### Missing coverage (no doc exists)
- [ ] <topic>: add spoke at <suggested path>

### Recommended order
1. ...
```

9. **Do not auto-edit** unless the user explicitly asks to implement the audit. Default deliverable is the todo list.

## Quality bar

- Cite specific file paths and line ranges when possible.
- Separate "verified OK" from issues so the user trusts what was checked.
- Prefer link-first fixes over copying content into hubs.
- Judge by token economy: the target state is hub + one spoke = enough context
  to make a well-fitting change; recommend splitting spokes that force
  whole-repo reading and merging spokes too thin to stand alone.
