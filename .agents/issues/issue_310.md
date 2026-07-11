---
id: issue-310
title: "Prevent workspace data loss during installation upgrades by preserving AGENTS.md, task board, and schemas"
status: closed
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
Prevent workspace data loss during installation upgrades by preserving the user's `AGENTS.md` config, tasks board `board.md`, database blueprint `schema.md`, and other workspace state configuration files.

## Tasks
- [x] Move issue-310 to Doing in task board <!-- id: task-move-board -->
- [x] Update install.py to exclude AGENTS.md and restore state files from backup <!-- id: task-update-install -->
- [x] Update bootstrap.py to prevent overwriting schema.md and board.md if they exist <!-- id: task-update-bootstrap -->
- [x] Add unit tests in test_install.py and test_bootstrap.py verifying data preservation <!-- id: task-unit-tests -->
- [x] Run validation tests and verify workspace compliance <!-- id: task-run-validation -->

## Acceptance Criteria
- [x] `install.py` excludes `AGENTS.md` from recursive copy overwrites. <!-- id: ac-agents-md-excluded -->
- [x] `install.py` restores all preserved workspace config and states from `.agents_backup_...` after copying core files. <!-- id: ac-restore-from-backup -->
- [x] `bootstrap.py` checks for the existence of `schema.md` and `board.md` and preserves them unless `force_update` is specified. <!-- id: ac-preserve-schema-board -->
- [x] All unit tests pass cleanly. <!-- id: ac-tests-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/tasks/board.md <!-- id: audit-target-board -->
  - [x] .agents/scripts/cli/commands/install.py <!-- id: audit-target-install -->
  - [x] .agents/scripts/cli/commands/bootstrap.py <!-- id: audit-target-bootstrap -->
  - [x] .agents/tests/test_install.py <!-- id: audit-target-test-install -->
  - [x] .agents/tests/test_bootstrap.py <!-- id: audit-target-test-bootstrap -->
  - [x] .agents/issues/issue_310.md <!-- id: audit-target-issue -->
- Active module locks:
  - [x] .agents/scripts/cli/commands/install <!-- id: lock-install -->
  - [x] .agents/scripts/cli/commands/bootstrap <!-- id: lock-bootstrap -->
  - [x] .agents/tests/test_install <!-- id: lock-test_install -->
  - [x] .agents/tests/test_bootstrap <!-- id: lock-test_bootstrap -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
