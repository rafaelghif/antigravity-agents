---
name: security
description: Use this skill when the user asks to modify authentication, authorization, CI/CD pipelines, Dockerfiles, handling user input, or touching secrets.
---

<CRITICAL_DIRECTIVE>
Execute the strict AppSec procedural audit.
</CRITICAL_DIRECTIVE>

<PROCEDURAL_WORKFLOW>
1. **Secret Scanning**: Before concluding, verify you have not hardcoded any credentials, tokens, or private keys.
2. **Boundary Audit**: If you added a new input vector (API endpoint, CLI argument), verify that a strict validation schema sits at the immediate boundary.
3. **Execution Context**: If modifying Dockerfiles or CI workflows, verify that execution privileges are explicitly dropped (`USER nonroot`).
4. **Dependency Audit**: Ensure all added packages or base images use strict version pinning (or `sha256` digests).
5. **Reporting**: Output a `<security_audit>` block confirming these checks are complete.
</PROCEDURAL_WORKFLOW>
