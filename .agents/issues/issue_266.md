---
id: issue-266
title: "fix target stack auto-detection and C# .NET core framework classification"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
fix target stack auto-detection and C# .NET core framework classification

## Tasks
- [x] fix stack auto-detection, add C# classification, and setup root projects.json <!-- id: task-1 -->

## Acceptance Criteria
- [x] unit tests pass and stack auto-detects correctly without python leak <!-- id: criteria-1 -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/scripts/recon.py <!-- id: audit-target-files -->
  - [x] .agents/tests/test_recon.py
- Active module locks:
  - [x] .agents/scripts/recon <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
