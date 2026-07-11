---
id: issue-262
title: "fix unit test failures in CI due to missing archive issues folder"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
fix unit test failures in CI due to missing archive issues folder

## Tasks
- [x] defensively wrap os.listdir calls with try-except to fix GHA unit test failures <!-- id: task-1 -->

## Acceptance Criteria
- [x] tests pass successfully locally and in mocked tests without crashing on missing archive directories <!-- id: criteria-1 -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/scripts/validate.py <!-- id: audit-target-files -->
  - [x] .agents/scripts/cli/commands/issue.py
- Active module locks:
  - [x] validate <!-- id: audit-module-locks -->
  - [x] .agents/scripts/cli/commands/issue <!-- id: lock-issue -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
