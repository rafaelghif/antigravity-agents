---
id: issue-084
title: "Fix upgrade command repository URL and update paths"
status: closed
assignee: agent-antigravity
created_at: 2026-06-28
---

# Issue Details

## Problem Statement
Fix upgrade command repository URL and update paths

## Tasks
- [x] Task 1: Create Pre-Implementation Impact Analysis and option decisions.
- [x] Task 2: Update SOURCE_REPO and paths_to_update in upgrade.py.
- [x] Task 3: Add unit tests to test_upgrade.py and verify all checks pass.

## Acceptance Criteria
- [x] upgrade.py points to https://github.com/rafaelghif/antigravity-agents.git.
- [x] upgrade.py includes .agents/skills/, .agents/rules.md, and AGENTS.md in paths_to_update.
- [x] All unit and integration tests pass successfully.
