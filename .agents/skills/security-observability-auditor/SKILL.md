---
name: security-observability-auditor
description: Code scanner for secrets, SAST, structured logging, and metrics verification.
instruction: Use before creating a PR or during reviews to scan code for hardcoded secrets, missing sanitization, and structured logging.
requires_core: ">=4.0.0"
---

# Security & Observability Auditor Skill

Enforces the Security and Observability Baselines defined in AGENTS.md.

## When to Execute
- BEFORE creating a PR (`git-workflow` step 5).
- During PR reviews for implementation changes.
- **Skip Condition**: If this is a `hotfix/` (SLA <2hr), you MUST still run the security audit, but you may skip non-critical observability refactors.

## Execution Steps

### 1. Secret Scanning
- Check if `gitleaks` is available. If not, fallback to executing via `npx gitleaks`.
- Ensure ALL environment variables are documented in `.agents/brain/env-required.json` (Schema: `{ "VAR_NAME": { "required": true, "secret": true, "description": "..." } }`) and accessed via `process.env` (or equivalent), not hardcoded. Validate all `required` vars are present before execution.

### 2. SAST (Static Application Security Testing)
- Check cache `.agents/brain/sast-<date>.json` before running. Skip if no new code changes.
- Execute the primary SAST tool by language:
  - Before running SAST, verify each tool is available (via `which` or `npx`). If missing, ask the user to install or proceed with fallback (`semgrep` always available via npx).
  - JS/TS: `eslint-plugin-security`, `npm audit`
  - Python: `bandit`, `safety`
  - Go: `gosec`
  - Java: `spotbugs`
  - Fallback: `semgrep`
- Check for common vulnerabilities and ensure input sanitization.

### 3. Observability Verification
- Verify the presence of structured JSON logging (check for `winston`, `pino`, etc., and verify `DEBUG` vs `PRODUCTION` env vars).
- Ensure ALL logs across all skill executions and application code output a `trace_id` for request correlation (see `.agents/common/utils.md`).
- Check that application metrics (`/metrics`) are exposed and updated correctly. Grep for `logger.error` or equivalent; verify that `process.env.NODE_ENV === 'production'` conditionally omits `stack` property, OR recommend using a logging library that automatically differentiates environments (e.g., `pino` with `redact`).

### 4. Remediation
- If any secrets are found, immediately halt, use `git reset`, and escalate.
- If SAST or Observability checks fail, refactor the code to comply before proceeding. **Remediation Timebox**: If remediation takes > `config.json -> timeouts.remediation_timebox_minutes`, escalate to user and document in `.agents/incidents/security-<date>.md`.
- Record the audit results in `.agents/brain/sast-<date>.json`.
