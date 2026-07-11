---
id: issue-302
title: "Add Task vs Discussion Distinction Rule"
status: closed
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
Add explicit guidelines and non-negotiable rules to distinguish between discussions/questions and actual task coding, preventing junk issue creation, branch checkouts, and commits for informational interactions.

## Tasks
- [x] Task 1: Add non-negotiable rule to AGENTS.md §2 <!-- id: task-agents-rule -->
- [x] Task 2: Add detailed guidelines in .agents/rules.md under Enterprise standards <!-- id: task-rules-guidelines -->
- [x] Task 3: Run validation guard checks and merge <!-- id: task-run-validation -->

## Acceptance Criteria
- [x] AGENTS.md contains non-negotiable rule distinguishing discussions vs tasks. <!-- id: ac-agents-rule -->
- [x] .agents/rules.md specifies that branch-and-issue workflow must only trigger for code/file edits. <!-- id: ac-rules-guidelines -->
- [x] Validation suite passes. <!-- id: ac-validation-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] AGENTS.md <!-- id: audit-target-files -->
  - [x] .agents/rules.md <!-- id: audit-target-files-2 -->
- Active module locks:
  - [ ] None <!-- id: lock-compliance -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
