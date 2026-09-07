---
name: accessibility-check
description: Audit a vibecoded app's UI for accessibility gaps — missing/wrong alt text, color-contrast failures, keyboard-inoperable controls and forms, and unclear button/link labels — using automated tooling when available and falling back to static code inspection otherwise. Produces a prioritized remediation checklist. Use when the user asks for an accessibility audit, a11y check, WCAG check, contrast check, or keyboard-navigation check.
---

# Accessibility Check

## Goal

Produce a **prioritized remediation checklist** with concrete evidence (`file:line`, or a screenshot/contrast ratio) for each finding — not a generic "add ARIA labels" sweep. Distinguish "verified passing," "verified failing," and "needs manual check" so the user knows what was actually tested versus inferred from code.

## Workflow

### 1. Check for existing tooling first

Prefer real tools over static grepping wherever they're available:

- **Lint-time:** `eslint-plugin-jsx-a11y` (React/JSX), `eslint-plugin-vuejs-accessibility` (Vue), or equivalent already configured? Run the existing lint command and read its a11y-rule output.
- **Runtime/live:** `axe-core`, `@axe-core/playwright`, `pa11y`, or Lighthouse CI already wired into tests or CI? Run them if a dev server can be started (see the `run` skill for how to launch this project).
- If nothing is configured, do the static checks below and separately recommend (don't silently install) `eslint-plugin-jsx-a11y` and a Playwright + `@axe-core/playwright` smoke test as one of the report's findings.

Automated tools catch far more real issues than code reading — use them whenever the project can run.

### 2. Static checks (when no live run is possible, or to supplement tooling)

**Images and alt text**
- Grep for `<img`, framework image components (`<Image`, `next/image`, etc.), and CSS `background-image` used to convey content (not pure decoration).
- Every meaningful image needs non-empty, descriptive `alt`. Decorative images should have `alt=""` (empty, not missing) or `role="presentation"` — flag `alt` that's missing entirely differently from `alt=""` used correctly.
- Flag alt text that's just the filename (`alt="IMG_2043.jpg"`) or redundant boilerplate (`alt="image"`).

**Color contrast**
- Extract color pairs (text color vs. background) from theme/CSS files, Tailwind config, or styled-components.
- Where a text/background pair is statically known (not computed at runtime from user data), compute the contrast ratio and check against WCAG AA: 4.5:1 for normal text, 3:1 for large text (≥18pt or ≥14pt bold) and UI components/graphical objects.
- Where colors are dynamic or theme-dependent (dark mode, computed styles), flag as "needs manual/live check" rather than guessing — don't report a pass or fail without a computed ratio.
- If a live run is possible, prefer an actual browser check (axe-core, or manual DevTools contrast checker on rendered pages) over static extraction.

**Keyboard operability**
- Flag interactive behavior on non-interactive elements: `onClick` on a `<div>`/`<span>` without a matching `role`, `tabIndex={0}`, and `onKeyDown` (Enter/Space) handler. Prefer flagging "use a `<button>`/`<a>` instead" over "add ARIA to a div" when the fix is that simple.
- Flag custom dropdowns, modals, and menus for focus management: does opening trap/move focus, does closing return it, is there an escape/close path via keyboard?
- Flag any positive `tabIndex` value (`tabIndex={1}`, `tabIndex={2}`, ...) — these break natural tab order and are almost always a bug, not an enhancement.
- Confirm forms are fully operable without a mouse: every input, checkbox, and submit control reachable and operable via Tab/Enter/Space, and validation errors are announced (not color-only, not visual-only).

**Labels**
- Every form `<input>`/`<select>`/`<textarea>` needs an associated `<label>` (via `for`/`id`, wrapping, or `aria-label`/`aria-labelledby`) — flag inputs relying on placeholder text alone as the label.
- Icon-only buttons/links need an accessible name (`aria-label`, visually-hidden text, or a `title` as a weaker fallback) — flag icon buttons with no text alternative.
- Flag ambiguous link/button text ("click here", "read more", "learn more", "submit") that doesn't describe the destination or action out of context — screen reader users often navigate by a list of link text alone.

### 3. Output format

```markdown
## Accessibility Check — <repo> — <date>

### Tooling used
- <axe-core / eslint-plugin-jsx-a11y / static inspection only> — <why>

### Verified passing
- <item> — <file:line or test run reference>

### Findings
| Severity | Category | Item | Evidence | Fix |
|----------|----------|------|----------|-----|
| High | Keyboard | Custom dropdown not operable via keyboard | `src/components/Menu.tsx:22` — `onClick` only, no `onKeyDown`/focus trap | Use a `<button>` trigger + roving tabindex or a listbox pattern |
| High | Contrast | Body text on card background fails AA (3.1:1) | `src/theme.css:14` `#8a8a8a` on `#f5f5f5` | Darken text to at least `#595959` (4.5:1) |
| Medium | Labels | Icon-only close button has no accessible name | `src/components/Modal.tsx:40` | Add `aria-label="Close"` |
| Low | Alt text | Hero image alt is the filename | `src/pages/Home.tsx:8` | Replace with a description of the image's content/purpose |

### Needs manual/live check
- <item> — <why static analysis couldn't verify it, and what to do to verify: e.g. "run with a screen reader", "check computed dark-mode contrast in DevTools">

### Recommended tooling additions
- <e.g. "add eslint-plugin-jsx-a11y to catch these at lint time going forward">

### Recommended order
1. ...
```

### 4. Do not auto-edit

Default deliverable is the report. Fix findings directly only when the user explicitly asks — and when you do, prefer the native-element fix (swap a `<div onClick>` for a `<button>`) over bolting on ARIA to fix a symptom.

## Quality bar

- Never report a contrast pass/fail without an actual computed ratio or a live tool's verdict — "looks fine" is not a finding.
- Distinguish `alt=""` (correct for decorative images) from missing `alt` (a real gap) — don't lump them together.
- Prefer fixing semantics (right element, real label) over adding ARIA to patch a non-semantic element, per the "first rule of ARIA."
- If the project has no way to run a live check, say so explicitly rather than presenting static-only findings as a complete audit.
