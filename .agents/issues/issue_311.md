---
id: issue-311
title: "Relax Clean Architecture and SOLID rules for simple/custom projects"
status: closed
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
We want to relax Clean Architecture and SOLID rules for simple/custom projects to maintain developer flexibility, allow a "none" scaffolding layout, and update the project rules.

## Tasks
- [x] Move issue-311 to Doing in task board <!-- id: task-move-board -->
- [x] Lock bootstrap and install modules <!-- id: task-lock-modules -->
- [x] Relax Clean Architecture rule in rules.md and its template <!-- id: task-relax-rules -->
- [x] Support none/custom arch in bootstrap.py and add unit test <!-- id: task-support-none-arch -->
- [x] Run validation tests and verify workspace compliance <!-- id: task-run-validation -->

## Acceptance Criteria
- [x] `rules.md` and `rules.md.template` contain the relaxed Clean Architecture and SOLID rule. <!-- id: ac-rules-relaxed -->
- [x] `bootstrap.py` supports the `"none"` architecture choice and skips scaffolding. <!-- id: ac-none-arch-supported -->
- [x] New test case `test_bootstrap_none_architecture` passes successfully. <!-- id: ac-tests-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/tasks/board.md <!-- id: audit-target-board -->
  - [x] .agents/scripts/cli/commands/bootstrap.py <!-- id: audit-target-bootstrap -->
  - [x] .agents/rules.md <!-- id: audit-target-rules -->
  - [x] .agents/templates/rules.md.template <!-- id: audit-target-template -->
  - [x] .agents/tests/test_bootstrap.py <!-- id: audit-target-test-bootstrap -->
  - [x] .agents/issues/issue_311.md <!-- id: audit-target-issue -->
- Active module locks:
  - [ ] .agents/scripts/cli/commands/bootstrap <!-- id: lock-bootstrap -->
  - [ ] .agents/scripts/cli/commands/install <!-- id: lock-install -->
  - [ ] bootstrap <!-- id: lock-bootstrap -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
