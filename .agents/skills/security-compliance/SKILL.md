---
name: security-compliance
description: Diagnostic playbook for scanning vulnerabilities, verifying secret exclusion, and executing OWASP Top 10 compliance audits. Package pinning, license auditing, upgrade verification, and package pruning playbook.
---

# Security & Compliance Playbook

This playbook outlines steps for auditing code changes against security guidelines, secret exposure risks, and library vulnerabilities, as well as managing dependencies.

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
- **Secure Storage**: Sensitive configuration files or API keys MUST NOT be globally stored in `~/.` or shared user folders on servers.

## 4. Package Auditing & Compliance
- **Package Pinning**: All dependencies in production applications MUST be pinned to exact versions (e.g. `1.2.3` instead of `^1.2.3` or `*`). This ensures reproducible builds and protects against supply chain attacks.
- **License Auditing**: Verify that third-party packages do not use restrictive copyleft licenses (like GPL) if the project is proprietary. Stick to MIT, Apache 2.0, or BSD licenses when possible.
- **Upgrade Verification**: When upgrading packages, always check the package's changelog for breaking changes and run the full test suite immediately.
- **Package Pruning**: Regularly scan for and remove unused dependencies from `package.json` or `requirements.txt` to minimize the attack surface.
