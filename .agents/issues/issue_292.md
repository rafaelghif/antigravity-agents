---
id: issue-292
title: "Synchronize CLI commands in context map documentation"
status: closed
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
The sitemap document `.agents/docs/context_map.md` is missing references to the `dashboard`, `doctor`, and `mcp` CLI commands, which are fully documented in the root `README.md` and supported by the codebase. We need to synchronize the documentation.

## Tasks
- [x] Add missing commands to `.agents/docs/context_map.md` <!-- id: task-sync-context-map -->
- [x] Run validation tests and verify code compliance <!-- id: task-run-validation -->

## Acceptance Criteria
- [x] `.agents/docs/context_map.md` contains entries for `dashboard`, `doctor`, and `mcp`. <!-- id: ac-context-map-updated -->
- [x] Validation checks pass cleanly. <!-- id: ac-validation-passes -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/docs/context_map.md <!-- id: audit-target-files -->
- Active module locks:
  - [ ] None <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
