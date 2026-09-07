---
name: legal-check
description: Audit a vibecoded app for legal, compliance, and business-risk gaps — privacy policy, terms & conditions, cookie policy/consent, refund policy, form consent, data minimization, analytics and third-party embed disclosure, unsubstantiated marketing claims and fake reviews, business details, image copyright, and applicable local-law risks — and produce a prioritized report with draft policy templates for anything missing. Use when the user asks for a legal check, compliance audit, pre-launch legal review, "am I going to get sued", or wants a privacy policy/terms/cookie policy drafted.
---

# Legal Check

## Goal

Produce a **prioritized gap report**, not blind edits or legal advice. Every finding says what's missing, why it matters, and — for missing policy pages — includes a ready-to-adapt draft. The user (or a follow-up session) decides what to implement.

This is not a substitute for a lawyer. Say so plainly wherever content is drafted.

## Not everything applies to every repo

Personal/vibecoded repos vary a lot: a static portfolio site doesn't need a refund policy, an app with no forms doesn't need form-consent language. Step 1 is always relevance detection — never run the full checklist blind, and always report what was excluded and why.

## Workflow

### 1. Establish context

Ask only what can't be inferred from the repo:

- What does this app do, and does it collect payment, run ads, target the EU/EEA/UK, or knowingly serve users under 13? Check `README.md`, `package.json` description, and landing/marketing copy first.
- Business name/entity, jurisdiction, and a support contact — needed for template placeholders. Check the footer, `/about`, and `/contact` before asking.

Don't ask about anything a grep can answer.

### 2. Detect applicability signals

| Signal to search for | Indicates | Relevant checklist items |
|---|---|---|
| `<form`, `onSubmit`, contact/signup/newsletter forms | User-submitted data | Form consent, data minimization |
| `stripe`, `checkout`, `paypal`, `price`, `subscription` | Payments | Refund policy, terms & conditions |
| `auth`, `login`, `signup`, `session`, user accounts | Accounts | Privacy policy, data minimization |
| `google-analytics`, `gtag`, `GA_MEASUREMENT`, `segment`, `mixpanel`, `posthog`, `plausible`, `amplitude` | Analytics | Cookie policy/consent, privacy policy |
| `facebook pixel`, `hotjar`, `sentry`, `clarity` | Tracking/monitoring | Cookie policy/consent, privacy policy |
| `<iframe`, `embed`, youtube/vimeo/maps/calendly/intercom/crisp/tawk | Third-party embeds | Privacy policy disclosure, possible cookie consent |
| `testimonial`, `review`, star ratings, "customers say" | Marketing claims | Fake reviews / substantiation |
| Superlatives: "guaranteed", "#1", "clinically proven", "risk-free", "cures", "instant" | Unsubstantiated claims | FTC-style substantiation |
| `privacy`, `terms`, `cookie`, `refund` in routes/pages | Existing policy pages | Verify content instead of drafting |
| `public/`, `assets/`, `images/` with stock or downloaded photos | Image provenance | Copyright check |
| Cookie consent libs (`cookieconsent`, `react-cookie-consent`, `vanilla-cookieconsent`, CookieYes/OneTrust script tags) | Consent already handled | Verify configuration instead of flagging missing |

Record what's present, partial, or absent with `file:line` evidence — verify first, same discipline as `doc-audit`.

### 3. Walk the checklist

For each applicable category, assess status (`present` / `partial` / `missing`) and note the risk of leaving it as-is.

**Pages & policies**
- Privacy policy — exists, reachable from footer/nav, and actually matches what's collected (not a stale generic copy)?
- Terms & conditions — covers acceptable use, liability, and account termination where relevant?
- Cookie policy & consent — does the app set non-essential cookies (analytics/ads/embeds)? If so, and any EU/EEA/UK/California audience is plausible, an opt-in consent banner is likely required, not just a notice.
- Refund policy — required if the app takes payment; check it's linked at or before checkout, not buried only in the ToS.
- Form consent — any form collecting personal data (especially marketing opt-in, health, or other sensitive categories) should have an explicit, unchecked-by-default consent checkbox linking to the privacy policy.

**Data practices**
- Data minimization — do signup/contact forms request fields the app doesn't actually use? Flag each unused required field individually.
- Analytics review — list every analytics/tracking tool detected; each one that collects personal data must be named in the privacy/cookie policy.
- Third-party embeds — list every embed; each is a potential data-sharing relationship that needs disclosure (and, in the EU, often consent before it loads).

Accessibility is a separate concern — hand off to the sibling `accessibility-check` skill rather than duplicating it here.

**Trust & marketing**
- Fake/unverifiable reviews — testimonials with no attribution, stock-photo "customers," or reviews untraceable to a real transaction are a real legal and platform-policy risk (FTC endorsement guidance, app store review policies). Flag for removal or real sourcing.
- Unsupported claims — flag superlative/absolute marketing language ("guaranteed," "clinically proven," "#1," "cures," "risk-free," "instant results") not backed by cited evidence anywhere in the repo/docs.

**Business identity**
- Business details — legal business name, a physical or registered address, and a real contact method should appear somewhere reachable (footer, about, or terms). Solo builders: at minimum a real contact email, not a no-reply address.

**Content rights**
- Image copyright — for each image under `public/`/`assets/`/similar, is there any record of its source or license (a credits file, alt text crediting the source, a filename suggesting a licensed stock service)? Flag images with no traceable provenance as a risk, especially any that look scraped or are AI-generated depictions of real people.

**Jurisdiction & other risk**
- Using the context from step 1 (audience geography, data collected, age of users, payment handling), name the *specific* regimes actually in play rather than listing all of them generically: GDPR only if EU/EEA/UK users are plausible, CCPA/CPRA only at California-relevant data-collection scale, COPPA only if under-13 users are plausible, PCI-DSS only if card data touches the app's own servers rather than a processor's hosted fields, CAN-SPAM/CASL only if the app sends marketing email. State explicitly when a regime does *not* apply and why — the report should never read as a generic disclaimer dump.

### 4. Draft missing policy content

For any of Privacy Policy, Terms & Conditions, Cookie Policy, Refund Policy, or Form Consent Notice marked `missing`, adapt the matching file in `templates/` using the business details and detected data practices/third parties from steps 1–2. Fill every placeholder — never leave `[Business Name]`-style brackets in the delivered draft. Keep the "not legal advice, have a professional review before publishing" note from the template intact and unedited.

Do not write drafts into the app's actual page/route files unless the user explicitly asks — deliver the draft content in the report. Wiring it into the app's routing/framework is a separate, repo-specific step for the user to confirm.

### 5. Output format

```markdown
## Legal Check — <repo> — <date>

Not legal advice — a compliance sanity check for a solo/small-team launch. Have a lawyer review anything here before relying on it, especially cross-border or payment-related items.

### Applies to this repo
- <detected signal> → <checklist items it triggers>

### Does not apply
- <checklist item> — <why, e.g. "no payment flow found">

### Findings
| Status | Item | Evidence | Risk if left as-is |
|--------|------|----------|---------------------|
| Missing | Cookie consent | Google Analytics loads unconditionally in `src/analytics.ts:12` | Non-essential tracking before consent — GDPR/UK-GDPR exposure if any EU traffic |
| Partial | Privacy policy | `src/pages/privacy.tsx` exists but doesn't mention Stripe or Sentry | Policy doesn't match actual data flows |

### Draft content
#### Privacy Policy
\`\`\`markdown
<adapted template>
\`\`\`
(repeat per missing policy page)

### Story-ready gaps
For each Missing/Partial finding, a ready-to-file story — paste straight into `stories/` via `story-creator`, or into a GitHub issue:

#### <Title>
**Goal:** ...
**Why:** ...
**Acceptance criteria:**
- [ ] ...

### Recommended order
1. ...
```

Use the `story-creator` body shape (Goal / Why / Acceptance criteria) for "Story-ready gaps" so entries need no reformatting to become real stories.

### 6. Do not auto-edit

Default deliverable is the report. Only create or modify files in the target repo (policy pages, consent banners, footer text) when the user explicitly asks to implement a specific finding.

## Quality bar

- Every finding cites evidence (`file:line`, or "not found after searching X, Y, Z") — no unverified claims.
- Never present a drafted policy as final or lawyer-reviewed; the disclaimer is not optional.
- Don't flag a jurisdiction's requirements as applicable without a concrete signal (audience, currency, data type) — generic "GDPR applies to everyone" padding erodes trust in the report.
- Fold accessibility findings into `accessibility-check`, not this report.
- Separate "applies" from "does not apply" so the user can see what was actually checked.
