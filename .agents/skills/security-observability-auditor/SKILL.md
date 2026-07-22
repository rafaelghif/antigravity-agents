---
name: security-observability-auditor
description: Scans code for hardcoded secrets, missing sanitization, and verifies structured logging and metrics.
---

# Security & Observability Auditor Skill

Enforces the Security and Observability Baselines defined in AGENTS.md §3.

## When to Execute
- BEFORE creating a PR (`git-workflow` step 6).
- During PR reviews for implementation changes.

## Execution Steps

### 1. Secret Scanning
- Run a secret scanner (e.g., `gitleaks detect` or `trufflehog`) against the changed files.
- Ensure ALL environment variables are documented in `.agents/brain/env-required.json` and accessed via `process.env` (or equivalent), not hardcoded.

### 2. SAST (Static Application Security Testing)
- Execute the primary SAST tool (e.g., CodeQL if available, or `eslint`/`pylint` with security plugins).
- Check for common vulnerabilities (e.g., SQL injection, XSS).
- Verify all user inputs are passed through framework-native sanitization libraries.

### 3. Observability Verification
- Verify the presence of structured JSON logging (INFO for production, DEBUG for development).
- Ensure critical paths output logs containing a `trace_id` for request correlation.
- Check that application metrics (e.g., Prometheus `/metrics`) are exposed and updated correctly.

### 4. Remediation
- If any secrets are found, immediately halt, use `git reset`, and escalate.
- If SAST or Observability checks fail, refactor the code to comply before proceeding.
- Record the audit results in `.agents/brain/sast-<date>.json`.
