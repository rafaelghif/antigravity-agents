---
id: issue-260
title: "fix git CI/CD validation job on main branch"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
fix git CI/CD validation job on main branch

## Tasks
- [x] fix branch alignment dirty check bypass on real CI/CD runner <!-- id: task-1 -->

## Acceptance Criteria
- [x] unit tests pass locally and CI validation passes without branch block <!-- id: criteria-1 -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/scripts/validate.py <!-- id: audit-target-files -->
- Active module locks:
  - [x] validate <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
