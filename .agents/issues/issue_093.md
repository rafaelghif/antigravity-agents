---
id: issue-093
title: "Implement incremental static analysis and unit testing in validation guard"
status: closed
assignee: agent-antigravity
created_at: 2026-06-28
---

# Issue Details

## Problem Statement
Implement incremental static analysis and unit testing in the validation guard to speed up commits and validation runs.

## Tasks
- [x] Task 1: Add get_modified_files utility function to validate.py
- [x] Task 2: Modify audit_static_linting to support incremental files checks
- [x] Task 3: Modify audit_unit_tests to skip tests if no code/test files changed
- [x] Task 4: Run unit tests and verify incremental validation works

## Acceptance Criteria
- [x] Statically compiles only modified scripts if active modifications are present.
- [x] Skips unit tests if only markdown/documentation files are modified.
- [x] Runs unit tests if python script files or tests are modified.
- [x] All local validation checks pass.
