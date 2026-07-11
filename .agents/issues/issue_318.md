---
id: issue-318
title: "docs: refactor readme to use professional engineering terminology and highlight concrete mechanisms"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
The README.md should be audited and refined to speak strictly in professional engineering terminology. Informal icons, fluff terminology (like Setup Interview, Zero-Trust Profiles, Visual Premium Dashboard), and any non-factual phrasing must be converted to professional equivalents that highlight concrete technical mechanisms.

## Tasks
- [x] Move issue-318 to Doing in task board <!-- id: task-move-board -->
- [x] Refactor README.md key features and introductory copy to use factual engineering terms <!-- id: task-edit-readme -->
- [x] Run validation tests and verify workspace compliance <!-- id: task-run-validation -->

## Acceptance Criteria
- [x] No informal marketing terms or non-factual descriptions remain in README.md. <!-- id: ac-phrasing-refined -->
- [x] Features are described by their exact underlying technical mechanisms (e.g. Local Git Author Rotation, Compliance Engine). <!-- id: ac-technical-mechanisms -->
- [x] All workspace validations pass cleanly. <!-- id: ac-tests-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/tasks/board.md <!-- id: audit-target-board -->
  - [x] README.md <!-- id: audit-target-readme -->
  - [x] .agents/issues/issue_318.md <!-- id: audit-target-issue -->
- Active module locks:
  - [x] readme <!-- id: lock-readme -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
