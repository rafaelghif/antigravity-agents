---
name: security-docs-auditor
description: Security SAST scanner, secret detector, and documentation synchronization engineer. Triggers when auditing security vulnerabilities, checking secrets, or updating README, API docs, and CHANGELOG.
requires_core: ">=4.2.0"
---
# Security & Documentation Auditor Skill

## Objective
Enforce strict security vulnerability scanning, secret leakage prevention, and technical documentation synchronization.

## 1. Security & Vulnerability Scanning (SAST)
- **Zero Hardcoded Secrets**: Scan codebase for leaked tokens, private keys, or API credentials.
- **SAST & Dependency Audits**: Run scanners (`semgrep`, `eslint-plugin-security`, `npm audit`, `pip-audit`). Block release if CVSS threshold $\ge 7.0$.

## 2. Documentation Synchronization
- **README & API Specs**: Keep `README.md` and OpenAPI/Swagger specs updated with code changes.
- **Strict SemVer CHANGELOG**: Update `CHANGELOG.md` following `[MAJOR.MINOR.PATCH]` semantic versioning. Verify version matches `package.json` / `pyproject.toml`.
- **Inline Documentation**: Enforce JSDoc / TSDoc / Python docstrings for public exported functions.
