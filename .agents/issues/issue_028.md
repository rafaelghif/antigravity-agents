---
id: issue-028
title: "Enforce strict git branch flow, merge procedures, and profile identity validation"
status: open
assignee: agent-antigravity
created_at: 2026-06-27
---

# Issue Details

## Problem Statement
Enforce strict git branch flow, merge procedures, and profile identity validation

## Tasks
- [x] Enforce strict branch checks in validate.py (prevent dirty changes on base branches and check issue patterns)
- [x] Update AGENTS.md and skills playbook to enforce branching and merging flow
- [x] Add unit tests for the branch validation changes

## Acceptance Criteria
- [x] All unit tests pass successfully
- [x] `./helper.sh validate` runs and passes successfully
