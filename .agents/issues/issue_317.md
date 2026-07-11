---
id: issue-317
title: "docs: update readme to remove unverified claims and use professional phrasing"
status: closed
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
The project README.md contains exaggerated/unverified claims such as "saving up to 80% in token budgets" and "under 100ms validation checks". These claims lack benchmark data and are unprofessional. They must be rephrased to focus on factual mechanisms (e.g. context optimization through active manifest updates, file load optimization, and efficient pre-commit validations).

## Tasks
- [x] Move issue-317 to Doing in task board <!-- id: task-move-board -->
- [x] Edit README.md to remove exaggerated token saving and latency claims <!-- id: task-edit-readme -->
- [x] Run validation tests and verify workspace compliance <!-- id: task-run-validation -->

## Acceptance Criteria
- [x] Exaggerated claims (80% token saving, under 100ms, premium label) are removed from README.md. <!-- id: ac-claims-removed -->
- [x] Descriptions focus strictly on actual features (context optimization, fast pre-commit checks). <!-- id: ac-factual-phrasing -->
- [x] Validation checks pass cleanly. <!-- id: ac-tests-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/tasks/board.md <!-- id: audit-target-board -->
  - [x] README.md <!-- id: audit-target-readme -->
  - [x] .agents/issues/issue_317.md <!-- id: audit-target-issue -->
- Active module locks:
  - [x] readme <!-- id: lock-readme -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
