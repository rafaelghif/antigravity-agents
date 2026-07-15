---
id: 339
title: "fix: restore dynamic placeholders in schema template to fix bootstrap test"
status: open
assignee: rafaelghif
created_at: 2026-07-15
---

# Issue Details

## Problem Statement
fix: restore dynamic placeholders in schema template to fix bootstrap test

## Tasks
- [x] Restore placeholders in .agents/templates/schema.md.template <!-- id: task-restore-placeholders -->
- [x] Update .agents/schema.md to reflect populated structure of the template for test-proj <!-- id: task-update-active-schema -->

## Acceptance Criteria
- [x] Unittests run successfully and pass all bootstrap command tests <!-- id: ac-unittests-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/templates/schema.md.template <!-- id: target-schema-template -->
  - [x] .agents/schema.md <!-- id: target-schema-md -->
- Active module locks:
  - [x] None <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
