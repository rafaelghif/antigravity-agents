---
name: security-audit
description: Diagnostic playbook for scanning vulnerabilities, verifying secret exclusion, and executing OWASP Top 10 compliance audits.
---

# Security & Vulnerability Auditing Skill

This playbook outlines steps for auditing code changes against security guidelines, secret exposure risks, and library vulnerabilities.

## 1. Secrets Leak Prevention
- **Scan Working Tree**: Search for hardcoded keys, passwords, bearer tokens, AWS IDs, or RSA keys before staging changes.
- **Gitignore Verification**: Ensure `.env` and other local credentials files are explicitly ignored in `.gitignore`.
- **Environment Templates**: Always document required environment variables in a generic template file (e.g. `.env.example`) containing placeholders rather than values.

## 2. Vulnerability Assessment Checklist
- **SQL Injections**: Check all database operations. Ensure queries use parameterized inputs or ORM safe-execution methods. Never concatenate raw strings inside database queries.
- **XSS (Cross-Site Scripting)**: Verify that user inputs are sanitized and escaped before rendering them in HTML or sending them to client applications.
- **Static Analysis (SAST)**: Use automated static code security scanners (e.g., `bandit` for Python, `eslint-plugin-security` for JavaScript/TypeScript, or CodeQL) to scan the codebase for structural vulnerabilities.
- **Insecure Dependencies**: Run dependency vulnerability scans:
  - For Node.js: `npm audit` or `pnpm audit`
  - For Python: `pip-audit` or `safety check`
  - For Go: `govulncheck ./...`

## 3. Deployment Security
- **Least Privilege**: Ensure network egress rules and API scopes are restricted to the bare minimum required for operations.
- **Secure Storage**: Sensitive configuration details must be fetched at runtime from secure environment stores (e.g. AWS Secrets Manager, GitHub Secrets) rather than baked into deployment images.

## 4. Exploit Prevention & Code Transparency

To guarantee that the agent installation is secure and does not compromise target repositories:
- **No Backdoors**: Never write code that bypasses authentication, provides unauthorized backdoors, or modifies files outside the designated project boundaries.
- **Supply Chain Security & Dependency Pinning**: Only install packages or libraries that are sourced from official registries (e.g. PyPI, npm). All packages must be pinned to exact versions (e.g., `requests==2.31.0` in `requirements.txt` or specific package lockfile hashes like `package-lock.json` or `poetry.lock`). Avoid dynamic range specifiers (like `*` or `>=`) to prevent dependency confusion attacks.
- **Code Transparency**: Deployed code must be clean, well-commented, human-readable, and completely free of obfuscation, dynamic execution (`eval()`), or unverified binary blobs.
- **Restricted System Access**: All installer scripts and validation hooks must perform operations strictly inside the workspace directory, preventing any interaction with user global home settings or non-workspace files.
