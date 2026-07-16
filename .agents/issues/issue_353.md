---
id: issue-353
title: "update readme with custom skill management and gitea features"
status: closed
assignee: rafaelghif
created_at: 2026-07-16
---

# Issue Details

## Problem Statement
update readme with custom skill management and gitea features

## Pre-Implementation Impact Analysis
- **Option A (Recommended)**: Update `README.md` to document the new `skill` CLI command subcommands, native Gitea integration, and offline registry fallbacks.
- **Option B**: Skip README updates, leaving major new features undocumented.

## Tasks
- [x] Task 1: Add documentation for the `skill` CLI command to the reference table in `README.md`. <!-- id: task-readme-command -->
- [x] Task 2: Highlight Gitea integration and offline registry caching features in the architectural overview/solutions table. <!-- id: task-readme-highlights -->
- [x] Task 3: Run validation to verify the README modifications are clean and correct. <!-- id: task-validate -->

## Acceptance Criteria
- [x] `README.md` is updated with complete reference and highlights of new features. <!-- id: ac-readme-updated -->
- [x] `./helper.sh validate` passes successfully. <!-- id: ac-validate -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] `README.md` <!-- id: target-readme -->
- Active module locks:
  - [ ] None <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
