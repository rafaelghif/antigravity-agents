---
id: issue-305
title: "Document prompt expansion and human approval flow in AGENTS.md"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
We need to explicitly document the prompt expansion (re-prompting) and human-in-the-loop approval constraints inside `AGENTS.md` to guarantee consistent agent behavior and prevent unauthorized or hallucinated executions.

## Tasks
- [x] Clean up duplicate task board line in board.md <!-- id: task-cleanup-board -->
- [ ] Update AGENTS.md to explicitly document the prompt expansion and human command approval flow <!-- id: task-update-agents-md -->
- [ ] Run validation tests and verify workspace compliance <!-- id: task-run-validation -->

## Acceptance Criteria
- [x] `board.md` has no duplicate entries for this issue. <!-- id: ac-board-clean -->
- [ ] `AGENTS.md` contains an explicit non-negotiable rule defining prompt expansion and human-in-the-loop command approvals. <!-- id: ac-agents-md-updated -->
- [ ] `./helper.sh validate` runs and passes cleanly. <!-- id: ac-validation-passes -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/tasks/board.md <!-- id: audit-target-board -->
  - [ ] AGENTS.md <!-- id: audit-target-agents -->
  - [ ] .agents/issues/issue_305.md <!-- id: audit-target-issue -->
- Active module locks:
  - [ ] None <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [ ] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [ ] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [ ] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
