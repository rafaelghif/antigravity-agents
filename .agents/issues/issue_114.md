---
id: issue-114
title: "Implement core robustness improvements: headless checks, parallel tests, utf-8 fixes, lockfile tracking, and json schema validation"
status: closed
assignee: agent-antigravity
created_at: 2026-07-02
---

# Issue Details

## Problem Statement
Implement core robustness improvements: headless checks, parallel tests, utf-8 fixes, lockfile tracking, and json schema validation

## Tasks
- [x] Implement non-interactive / headless check in CLI interactive prompting
- [x] Implement process-pool parallel monorepo test execution in validate.py
- [x] Add lockfile / dependency tracking to incremental check in validate.py
- [x] Implement lightweight schema validation for JSON configuration files
- [x] Run full workspace validation and close issue

## Acceptance Criteria
- [x] Non-interactive prompts throw runtime error if run headless.
- [x] Monorepo tests run concurrently using ProcessPoolExecutor.
- [x] Changes to lockfiles trigger full linting and tests in validate.py.
- [x] JSON configuration files are strictly schema-validated at load time.
- [x] All workspace tests and validation audits pass cleanly.
