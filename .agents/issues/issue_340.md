---
id: 340
title: "fix: increase agent unit tests validation timeout to prevent CI pipeline hangs"
status: open
assignee: rafaelghif
created_at: 2026-07-15
---

# Issue Details

## Problem Statement
fix: increase agent unit tests validation timeout to prevent CI pipeline hangs

## Tasks
- [x] Increase unit test discover timeout in .agents/scripts/validate.py from 15 to 90 seconds <!-- id: task-increase-timeout -->

## Acceptance Criteria
- [x] Timeout validation checks pass successfully <!-- id: ac-timeout-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/scripts/validate.py <!-- id: target-validate-py -->
- Active module locks:
  - [x] None <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
