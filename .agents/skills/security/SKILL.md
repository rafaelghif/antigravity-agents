---
name: security
description: Use this skill when the user asks to modify authentication, authorization, CI/CD pipelines, Dockerfiles, handling user input, or touching secrets.
---

<CRITICAL_DIRECTIVE>
Execute strict AppSec procedural audits and mandate ZERO-TOLERANCE for dummy authentication or authorization logic.
</CRITICAL_DIRECTIVE>

<ENTERPRISE_STANDARDS>
1. **ZERO Dummy Auth**: You are strictly FORBIDDEN from using hardcoded roles (e.g., `if user.role == 'admin'`) or dummy data. You MUST implement industrial-standard Policy-Based Access Control (PBAC), Attribute-Based Access Control (ABAC), or a robust RBAC system backed by actual database relations.
2. **Industrial Cryptography**: NEVER use mock hashes or plain-text passwords. You MUST integrate production-grade cryptography (e.g., Argon2id, bcrypt, or framework-native secure hashers) and fully implement JWT/Session validation.
3. **Strict Schema Fidelity**: DO NOT hallucinate User, Role, or Permission tables. You MUST use `grep_search` to verify the exact database schema or Prisma/TypeORM/SQL models before writing authorization logic.
</ENTERPRISE_STANDARDS>

<PROCEDURAL_WORKFLOW>
1. **Automated Scanning**: Execute `gitleaks detect` or `semgrep scan` on your diffs before concluding the security audit. Do not rely solely on visual inspection. If tools are unavailable, explicitly note this in your report.
2. **Secret Scanning & Git Hygiene**: Ensure all credentials, tokens, and private keys are strictly referenced via environment variables. Run `python3 scripts/git_hygiene_guard.py --check` to ensure zero untracked secrets or dirty stashes.
3. **Boundary Audit**: If you added a new input vector (API endpoint, CLI argument), verify that a strict validation schema sits at the immediate boundary.
4. **Execution Context**: If modifying Dockerfiles or CI workflows, verify that execution privileges are explicitly dropped (`USER nonroot`).
5. **Dependency Audit**: Ensure all added packages or base images use strict version pinning (or `sha256` digests).
6. **Shell Isolation (Terminal-First Security)**: You are FORBIDDEN from executing global installs (`npm i -g`, `sudo`), modifying SSH keys, or running destructive recursive commands (`rm -rf /`). All shell execution MUST be isolated to the project workspace.
7. **Verification & Audit Report**: Run `python3 scripts/verify.py --execute` and output a `<security_audit>` block confirming these checks are complete.
</PROCEDURAL_WORKFLOW>


<L9_STANDARDS>
- **Zero Trust**: Always sanitize and validate input payloads. Never trust client-side validation.
- **Secrets Management**: Never hardcode credentials. Always use environment variables or secret managers.
- **OWASP Top 10**: Protect against SQL Injection, XSS, CSRF, and IDOR by default.
</L9_STANDARDS>
