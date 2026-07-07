---
name: doc-audit
description: Audit documentation for staleness, broken links, and hub-and-spoke violations against recent code changes. Use when the user asks for a documentation audit, doc drift check, link-first refresh, AI-context audit, or wants to verify README and spoke docs still match the codebase.
---

# Documentation Audit

## Goal

Produce a **remediation todo list** — not blind edits. Verify first, then recommend fixes.

## Workflow

1. **Map the doc layout**
   - Find hub docs: `README.md`, `AGENTS.md`, `CLAUDE.md`, `.claude/README.md` or `HUB.md`.
   - Find spoke docs: `.claude/*.md`, `.cursor/*.md`, `.cursor/rules/*`, `docs/`.
   - Note hub-and-spoke rules if present (e.g. "README is navigation only; details live in spokes").

2. **Identify recent code changes**
   - Run `git log --oneline -20` and `git diff --stat HEAD~20..HEAD` (adjust depth if user specifies a range or branch).
   - List modules, CLI flags, env vars, API routes, or CI steps that changed.

3. **Cross-check docs vs code**
   For each changed area, check whether spokes mention it:
   - CLI subcommands/options → `.claude/CLI.md` or equivalent
   - Env vars → `.claude/ENV.md` / `.env.example`
   - Web routes → `.claude/WEB.md`
   - CI/deploy → `.claude/CICD.md`
   - Architecture moves → `.claude/ARCHITECTURE.md`

4. **Link audit**
   - Scan markdown for `[text](path)` and `` [`path`](path) `` links.
   - Flag broken relative links (target file missing).
   - Flag hub docs that duplicate long spoke content instead of linking.
   - Flag spokes with no back-link to hub where the project expects bidirectional links.

5. **Output format**

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

### Missing coverage (no doc exists)
- [ ] <topic>: add spoke at <suggested path>

### Recommended order
1. ...
```

6. **Do not auto-edit** unless the user explicitly asks to implement the audit. Default deliverable is the todo list.

## Quality bar

- Cite specific file paths and line ranges when possible.
- Separate "verified OK" from issues so the user trusts what was checked.
- Prefer link-first fixes over copying content into hubs.
