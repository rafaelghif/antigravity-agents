---
id: issue-032
title: "Enforce strict module lock verification gate in validation checks"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Issue Details

## Problem Statement
While there is a rule to acquire locks before editing modules, it is currently not programmatically enforced. We need to implement a strict lock verification check in the validation guard to block staging/committing modified source files unless a module lock is held by the current branch.

## Tasks
- [x] Implement check_staged_locks function in validate.py to audit staged files against locks.json
- [x] Add lock verification step to run_validations pipeline in validate.py
- [x] Update unit tests in test_validate.py to cover lock validation success and failure cases
- [x] Validate and close issue-032 using the automated issue close command

## Acceptance Criteria
- [x] Validator fails if any staged python file (outside tests/plans) is modified but not locked by the current branch
- [x] Validator fails if a staged file is locked by a different branch
- [x] Validator passes if all staged python files are correctly locked by the current branch
