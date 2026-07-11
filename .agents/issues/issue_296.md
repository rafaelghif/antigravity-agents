---
id: issue-296
title: "Document prompt expansion and human approval flow in AGENTS.md"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
We need to explicitly document the prompt expansion (re-prompting) and human-in-the-loop approval constraints inside `AGENTS.md` to guarantee consistent agent behavior and prevent unauthorized or hallucinated executions.

## Tasks
- [x] Add prompt expansion and human approval rules to `AGENTS.md` <!-- id: task-update-agents-md -->
- [x] Run validation tests and verify code compliance <!-- id: task-run-validation -->

## Acceptance Criteria
- [x] `AGENTS.md` contains a non-negotiable rule enforcing prompt expansion and human approval checks. <!-- id: ac-agents-md-updated -->
- [x] Validation checks pass cleanly. <!-- id: ac-validation-passes -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] AGENTS.md <!-- id: audit-target-files -->
- Active module locks:
  - [ ] None <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
