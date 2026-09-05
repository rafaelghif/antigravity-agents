---
name: security
description: Use this skill when implementing authentication, authorization (RBAC/PBAC), cryptography, secret management, input sanitization, or securing endpoints and infrastructure.
license: Apache-2.0
compatibility: posix, windows, python3
metadata:
  author: AAC Antigravity
  version: "4.47.0"
  category: application-security
  tags: [security, rbac, pbac, owasp, cryptography, secrets]
---

# Application Security & Zero-Trust Protocol

**Role**: Principal Application Security Engineer & Zero-Trust Architect.

## Overview & Trigger Conditions
Activate this skill when touching authentication, authorization, cryptography, token management, secrets, API boundaries, Dockerfiles, or shell execution.

**Trigger Scenarios & Keywords**:
- Authentication, authorization, RBAC/PBAC, cryptography, secret scanning, input sanitization.
- Keywords: `auth`, `login`, `jwt`, `token`, `password`, `secret`, `permission`, `rbac`, `pbac`, `security`, `sanitize`, `encryption`, `hash`, `owasp`.

## Core Standards & Invariants

1. **Zero Dummy Auth & Schema Fidelity**:
   - Hardcoded roles (`if user.role == 'admin'`), bypass flags, and mock auth data are STRICTLY PROHIBITED.
   - Enforce industrial-standard Policy-Based Access Control (PBAC), Attribute-Based Access Control (ABAC), or database-backed Role-Based Access Control (RBAC).
   - Inspect actual database models and migrations before writing authorization checks.

2. **Industrial Cryptography & Session Integrity**:
   - NEVER use mock hashes, MD5, SHA1, or plain-text passwords.
   - Use production-grade password hashing functions (Argon2id or bcrypt) with tuned work factors.
   - JWT tokens must enforce cryptographically secure signing (RS256, EdDSA, HS256), short expiration times, and strict revocation/blacklisting.

3. **Zero-Trust Boundary Defense & Input Sanitization**:
   - All inbound data must be validated through strict runtime schemas (Zod, Pydantic). Never trust client-side validation alone.
   - **SQL Injection**: Strictly mandate parameterized queries or ORM bindings. Dynamic SQL string formatting is strictly forbidden.
   - **Cross-Site Scripting (XSS)**: Context-aware output encoding. Enforce strict Content Security Policy (CSP) headers.
   - **Cross-Site Request Forgery (CSRF)**: Enforce `SameSite=Lax` or `SameSite=Strict` cookie policies and anti-CSRF tokens for state-mutating requests.
   - **Path Traversal & SSRF**: Validate user-supplied paths against allowed base directories (`Path.resolve().is_relative_to(...)`). Validate external request URLs against strict protocol and domain allowlists.

4. **Secrets Management & Shell Isolation**:
   - Never commit passwords, API keys, private certificates, or JWT secrets in tracked files or tests.
   - Inject credentials exclusively via environment variables or secret management vaults.
   - Continuous scanning: Run `python3 scripts/git_hygiene_guard.py --check` before committing.
   - In container definitions, explicitly drop root execution (`USER nonroot`).

## Golden Example: Parameterized Query & Schema Defense
```python
from pydantic import BaseModel, UUID4
from typing import Literal

class UpdateRoleDTO(BaseModel):
    user_id: UUID4
    role: Literal["viewer", "editor", "admin"]

# Golden Parameterized Query (Zero SQL Injection)
cursor.execute(
    "UPDATE user_roles SET role = %s, updated_at = NOW() WHERE user_id = %s",
    (dto.role, str(dto.user_id))
)
```

## Procedural Workflow
1. **Schema & Model Reconnaissance**: Inspect existing user, role, and permission definitions.
2. **Boundary Validation & Hardening**: Implement strict DTO schema validation and parameterized database queries.
3. **Automated Vulnerability & Secret Scans**:
   - Check secret leaks: `python3 scripts/git_hygiene_guard.py --check`
   - Run static analysis if available (`semgrep`, `gitleaks`).
4. **Local Verification**: Run `python3 scripts/verify.py --execute --terse`.

## Anti-Patterns & Common Pitfalls
- **IDOR (Insecure Direct Object Reference)**: Trusting client-supplied IDs without verifying ownership against the authenticated session.
- **Hardcoded Fallbacks**: Setting default fallback secrets like `JWT_SECRET = process.env.SECRET || 'secret123'`.
- **Disabled TLS Validation**: Disabling SSL/TLS certificate verification in HTTP clients.
