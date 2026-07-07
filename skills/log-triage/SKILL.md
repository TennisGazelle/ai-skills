---
name: log-triage
description: Structured root-cause analysis for pasted error logs, CI failures, Docker output, and AWS/IAM/S3/Lambda errors. Use when the user pastes a stack trace or log and asks why it failed, what went wrong, or how to fix a deployment/CI/runtime error.
---

# Log Triage

## Goal

Turn pasted logs into a **structured diagnosis**: symptom → likely cause → verification step → fix — verify before assuming.

## Workflow

1. **Extract signals from the log**
   - Error type / exit code
   - First failing line (not last — root cause often appears earlier)
   - Service names (container, Lambda, EC2, GH Action job)
   - Permission errors (`AccessDenied`, `403`, `Unauthorized`)
   - Missing resource errors (`NotFound`, `NoSuchKey`, `EntityNotFound`)

2. **Classify failure category**

| Category | Common signatures |
|----------|-------------------|
| **IAM / permissions** | `AccessDenied`, `is not authorized to perform`, wrong role ARN |
| **S3 cross-account** | `ListBucket` denied, `GetObject` denied, bucket policy vs identity policy mismatch |
| **Network / SG** | connection timeout, `Connection refused`, SSH hang |
| **CI dependency** | `npm ERR`, `playwright install`, missing browser, cache miss |
| **Docker / compose** | container exit, volume mount, env var missing in service |
| **DB / migration** | Flyway, connection refused to RDS, auth failure |
| **Config / env** | undefined variable, wrong profile, stale `.env` |

   See [references/failure-patterns.md](references/failure-patterns.md) for expanded checklists.

3. **Verify before fixing (required)**
   For the top 1–2 hypotheses, state what command or check confirms/denies it. Do not jump to code changes until the user confirms or you run the check.

4. **Output format**

```markdown
## Log Triage

### Symptom
<one sentence>

### Key lines
```
<quoted log excerpt>
```

### Likely cause (ranked)
1. **...** — because ...
2. **...** — because ...

### Verify
- [ ] Run/check: `...` — expect ...

### Fix (after verified)
- ...

### If still failing
- Next checks: ...
```

5. **Repo context**
   - If working in a known repo (arbor, benchmarking-iac), cross-check `.claude/ENV.md`, `.claude/CICD.md`, or `.claude/S3_LAMBDA_RDS.md` before guessing AWS layout.

## Quality bar

- Quote the log; do not paraphrase error messages loosely.
- Separate "verify" from "fix" — matches the user's `(a) verify (b) then act` pattern.
- If the log is truncated, say what additional lines would help.
