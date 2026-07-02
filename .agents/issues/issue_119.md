---
id: issue-119
title: "Refactor helper doctor key check validation to warnings instead of hard failures"
status: closed
assignee: agent-antigravity
created_at: 2026-07-02
---

# Issue Details

## Problem Statement
Refactor helper doctor key check validation to warnings instead of hard failures

## Tasks
- [x] Modify doctor.py to change SSH/GPG file/key checks from hard errors (False) to warnings (True)
- [x] Verify validations pass and close task

## Acceptance Criteria
- [x] running ./helper.sh doctor completes successfully (exit code 0) even with mock profiles.
- [x] SSH/GPG checks print a warning instead of failing the doctor run.
- [x] Local validation guard passes cleanly.
