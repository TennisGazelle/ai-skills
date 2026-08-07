---
name: ponytail-help
description: >
  Quick-reference card for all ponytail modes, skills, and commands.
  One-shot display, not a persistent mode. Trigger: /ponytail-help,
  "ponytail help", "what ponytail commands", "how do I use ponytail".
---

> **Source:** Vendored from [`lib/ponytail`](../../lib/ponytail) ([DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)). Refresh with `./scripts/submod-parity.sh`.

# Ponytail Help

Display this reference card when invoked. One-shot, do NOT change mode,
write flag files, or persist anything.

## Levels

| Level | Trigger | What change |
|-------|---------|-------------|
| **Lite** | `/ponytail lite` | Build what's asked, name the lazier alternative in one line. |
| **Full** | `/ponytail` | The ladder enforced: YAGNI → stdlib → native → one line → minimum. Default. |
| **Ultra** | `/ponytail ultra` | YAGNI extremist. Deletion before addition. Challenges requirements before building. |

Level sticks until changed or session end.

## Skills

| Skill | Trigger | What it does |
|-------|---------|--------------|
| **ponytail** | `/ponytail` | Lazy mode itself. Simplest solution that works. |
| **ponytail-review** | `/ponytail-review` | Over-engineering review: `L42: yagni: factory, one product. Inline.` |
| **ponytail-audit** | `/ponytail-audit` | Whole-repo over-engineering audit: ranked list of what to delete. |
| **ponytail-debt** | `/ponytail-debt` | Harvest `ponytail:` shortcut comments into a tracked ledger. |
| **ponytail-gain** | `/ponytail-gain` | Measured-impact scoreboard: less code, less cost, more speed. |
| **ponytail-help** | `/ponytail-help` | This card. |

Codex uses `@ponytail`, `@ponytail-review`, and `@ponytail-help`; Claude Code
and OpenCode use the slash-command forms above (OpenCode ships all six as
slash commands).

## Recommended order

No single workflow forces all six together, but if you're running the whole
family against a repo (e.g. "audit this codebase with ponytail"), this order
matches how the skills actually depend on each other:

1. **`ponytail-help`** (this card) — orientation, no dependency, safe to check
   anytime.
2. **`ponytail`** — the only skill that *writes* anything: code plus
   `ponytail: <ceiling>, <upgrade path>` comments as shortcuts accumulate.
   Only relevant when writing new code; it has nothing to do against a
   codebase that already exists and wasn't built under it.
3. **`ponytail-audit`** — whole-repo over-engineering scan. Independent of
   step 2's markers, so it's the right first read on existing code.
4. **`ponytail-debt`** — harvests the `ponytail:` markers step 2 leaves
   behind. Run after step 2 has had a chance to run; on a codebase that
   was never built under `ponytail`, this correctly reports a clean ledger.
5. **`ponytail-gain`** — static scoreboard, shown last since its own output
   points back to steps 3-4 ("This repo: /ponytail-debt ... /ponytail-audit
   ...") for the real per-repo numbers.

`ponytail-review` (diff-scoped, not listed above) runs whenever there's a
diff to review — it doesn't fit the whole-repo sequence, use it per PR/change
instead.

## Deactivate

Say "stop ponytail" or "normal mode". Resume anytime with `/ponytail`.
`/ponytail off` also works.

## Configure Default Mode

Default mode = `full`, auto-active every session. Change it:

**Environment variable** (highest priority):
```bash
export PONYTAIL_DEFAULT_MODE=ultra
```

**Config file** (`~/.config/ponytail/config.json`, Windows: `%APPDATA%\ponytail\config.json`):
```json
{ "defaultMode": "lite" }
```

Set `"off"` to disable auto-activation on session start, activate manually
with `/ponytail` when wanted.

Resolution: env var > config file > `full`.

## Update

This catalog vendors ponytail from the `lib/ponytail` submodule. Refresh with:

```bash
./scripts/submod-parity.sh
```

Or invoke the `submod-parity` skill. That checks out the submodule branch matching
the parent branch (`master`↔`main` alias), re-copies skills into `skills/`, and
refreshes `CATALOG.md`. Do not use Claude Code `/plugin` marketplace update for
these vendored copies.

## More

Full docs + examples: https://github.com/DietrichGebert/ponytail
