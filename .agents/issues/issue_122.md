---
id: issue-122
title: "Fix security vulnerabilities and performance bottlenecks identified in critical audit"
status: open
assignee: agent-antigravity
created_at: 2026-07-02
---

# Issue Details

## Problem Statement
Fix security vulnerabilities and performance bottlenecks identified in critical audit

## Tasks
- [x] Task 1: Add timeout to urllib urlopen requests in git_api.py
- [x] Task 2: Eliminate shell=True implicit shell injection in validate.py test execution
- [x] Task 3: Secure npx formatting and linting fallbacks using --no-install in validate.py
- [x] Task 4: Cap ThreadPoolExecutor workers in validate.py to avoid CPU thrashing

## Acceptance Criteria
- [x] No urlopen request in git_api.py is missing a timeout
- [x] Implicit shell execution is replaced by safe/explicit argument lists
- [x] npx fallback uses --no-install to enforce local/offline execution only
- [x] ThreadPoolExecutor workers are capped using os.cpu_count()
- [x] All tests and validations pass cleanly
