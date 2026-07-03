---
id: issue-148
title: "Fix integration test auto-upgrade hang on main branch"
status: closed
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
Fix integration test auto-upgrade hang on main/master branch where git fetch might hang on auth/network prompts.

## Tasks
- [x] Add IN_AUDIT_TEST environment check to check_and_run_auto_upgrade in upgrade.py
- [x] Add timeout=15 to unit test execution subprocess in validate.py
- [x] Verification complete

## Acceptance Criteria
- [x] Validation does not hang on unit tests
- [x] Unit tests pass successfully on base branches without hanging
