---
id: issue-308
title: "Enhance solo workflow mode to bypass lock and branch alignment checks"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
We need to relax the local validation rules for developers working in "solo" mode (`workflow_mode: solo` in `.agents/config.json`). Specifically, we should bypass module lock compliance checks and git branch-to-issue alignment checks so solo developers can work faster without the overhead of creating issues and locking files.

## Tasks
- [x] Move issue-308 to Doing in task board <!-- id: task-move-board -->
- [x] Implement get_workflow_mode() in validate.py <!-- id: task-implement-helper -->
- [x] Update audit_git_branch_alignment to bypass in solo mode <!-- id: task-update-branch-audit -->
- [x] Update audit_module_locks to bypass in solo mode <!-- id: task-update-lock-audit -->
- [x] Run validation tests and verify workspace compliance <!-- id: task-run-validation -->

## Acceptance Criteria
- [x] `validate.py` retrieves the correct `workflow_mode` configuration. <!-- id: ac-workflow-mode-retrieved -->
- [x] Git branch to issue alignment check is bypassed when `workflow_mode == "solo"`. <!-- id: ac-branch-bypass -->
- [x] Module lock compliance check is bypassed when `workflow_mode == "solo"`. <!-- id: ac-lock-bypass -->
- [x] Local tests and validator pass cleanly. <!-- id: ac-tests-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/tasks/board.md <!-- id: audit-target-board -->
  - [x] .agents/scripts/validate.py <!-- id: audit-target-validate -->
  - [x] .agents/tests/test_validate.py <!-- id: audit-target-test-validate -->
  - [x] .agents/issues/issue_308.md <!-- id: audit-target-issue -->
- Active module locks:
  - [x] .agents/scripts/validate <!-- id: lock-validate -->
  - [x] .agents/tests/test_validate <!-- id: lock-test_validate -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
