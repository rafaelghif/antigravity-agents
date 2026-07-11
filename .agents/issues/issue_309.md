---
id: issue-309
title: "Optimize context optimizer for solo workflow mode and improve token efficiency ratings"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
We need to enhance the context optimizer command script (`.agents/scripts/cli/commands/context.py`) to fully support the `"solo"` workflow mode. Currently, it crashes with an error if executed on base branch main/master or a branch without a valid issue pattern. We should relax these base branch and issue ID constraints in solo mode, fallback to default labels, and add testing.

## Tasks
- [x] Move issue-309 to Doing in task board <!-- id: task-move-board -->
- [x] Lock modified modules and verify locks <!-- id: task-acquire-locks -->
- [x] Update context.py to support workflow_mode == solo <!-- id: task-update-context -->
- [x] Add unit tests in test_context.py verifying solo mode context optimization <!-- id: task-unit-tests -->
- [x] Run validation tests and verify workspace compliance <!-- id: task-run-validation -->

## Acceptance Criteria
- [x] `context.py` successfully executes on base branches or arbitrary branches when `workflow_mode == "solo"`. <!-- id: ac-context-solo-executed -->
- [x] A generic `SOLO-WORKFLOW` issue ID and details are used as fallback when no issue ID is matched. <!-- id: ac-fallback-used -->
- [x] All unit tests in `test_context.py` pass cleanly. <!-- id: ac-tests-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/tasks/board.md <!-- id: audit-target-board -->
  - [x] .agents/scripts/cli/commands/context.py <!-- id: audit-target-context -->
  - [x] .agents/tests/test_context.py <!-- id: audit-target-tests -->
  - [x] .agents/issues/issue_309.md <!-- id: audit-target-issue -->
- Active module locks:
  - [x] .agents/scripts/cli/commands/context <!-- id: lock-context -->
  - [x] .agents/tests/test_context <!-- id: lock-test_context -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
