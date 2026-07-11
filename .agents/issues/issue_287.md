---
id: issue-287
title: "Fix branch naming friction and flexible issue closing resolution"
status: closed
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
The V3 system currently enforces strict regex matches for branch names containing issue IDs (e.g. `feat/issue-123`). This introduces friction:
1. Pure numbers in branch names (like `feat/287`) fail validation.
2. The `issue close` command expects exact slug-based branch structures and fails if the branch name has description suffixes (like `feat/issue-285-some-desc`).

We need to make this matching logic extremely flexible.

## Tasks
- [x] Implement flexible ID extraction (supporting pure numbers and various formats) in `.agents/scripts/validate.py` <!-- id: task-update-validate -->
- [x] Implement branch discovery in `.agents/scripts/cli/commands/issue.py` by querying git branches to find any branch containing the target issue ID <!-- id: task-update-issue -->
- [x] Run validation tests and verify code compliance <!-- id: task-run-tests -->

## Acceptance Criteria
- [x] Validation guard accepts branch name formats like `feat/287`, `feat/issue287`, or `feat/issue-287`. <!-- id: ac-validate-formats -->
- [x] `issue close` correctly matches branches containing descriptions (e.g. `feat/issue-287-friction`). <!-- id: ac-close-matches -->
- [x] All unit tests pass successfully. <!-- id: ac-tests-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/scripts/validate.py <!-- id: audit-validate-file -->
  - [x] .agents/scripts/cli/commands/issue.py <!-- id: audit-issue-file -->
- Active module locks:
  - [ ] .agents/scripts/validate <!-- id: lock-validate -->
  - [ ] .agents/scripts/cli/commands/issue <!-- id: lock-issue -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
