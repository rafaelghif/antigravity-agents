---
id: issue-085
title: "Implement Auto-Task ID Injection via prepare-commit-msg Git hook"
status: closed
assignee: agent-antigravity
created_at: 2026-06-28
---

# Issue Details

## Problem Statement
Implement Auto-Task ID Injection via prepare-commit-msg Git hook

## Tasks
- [x] Task 1: Create Pre-Implementation Impact Analysis and option decisions.
- [x] Task 2: Implement .agents/scripts/prepare_commit_msg.py with branch parsing and message injection.
- [x] Task 3: Update bootstrap.sh, bootstrap.ps1, and bootstrap.py to install the prepare-commit-msg Git hook.
- [x] Task 4: Add unit tests to test_prepare_commit_msg.py and verify all checks pass.

## Acceptance Criteria
- [x] Committing from a branch like feat/issue-085 automatically appends "Refs: issue-085" to the commit message.
- [x] If GPG or git commit --amend or manual message editor runs, it handles the message correctly.
- [x] All unit and integration tests pass successfully.
