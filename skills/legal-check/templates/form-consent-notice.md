> **Not legal advice.** Use this as starting copy for a consent checkbox/notice next to a form, not as a standalone page. The checkbox itself must be unchecked by default — pre-checked consent is invalid in most jurisdictions that regulate consent at all.

# Form Consent Notice (component copy, not a page)

## Standard data-collection notice

Place directly below or beside the form fields, in the same visual context (not just linked from elsewhere):

> By submitting this form, you agree to our [Privacy Policy](/privacy-policy) and consent to [Business Name] collecting and processing the information above to [specific purpose — e.g. "respond to your inquiry"].

## Marketing opt-in (separate, unchecked checkbox — never bundled with the notice above)

```html
<label>
  <input type="checkbox" name="marketing_opt_in" required={false} checked={false} />
  I'd like to receive occasional product updates by email. You can unsubscribe anytime.
</label>
```

Marketing consent must be its own explicit action, separate from "I agree to the Privacy Policy" — bundling them (or requiring the marketing checkbox to submit the form) turns a valid consent into an invalid one in most consent-regulating jurisdictions.

## Sensitive data (health, financial, biometric, etc.)

If a form collects any sensitive category of data, add an explicit, specific consent statement naming the category and purpose — a generic "I agree to the Privacy Policy" checkbox is not sufficient:

> I consent to [Business Name] collecting my [specific data type, e.g. "health information"] for the purpose of [specific purpose]. I understand I can withdraw this consent at any time by contacting [Contact Email].

## Fields to actually include

Before wiring this notice to a form, confirm every requested field is used somewhere in the app. Delete any field that exists "just in case" — each one is a data-minimization gap, not just a UX nit.
