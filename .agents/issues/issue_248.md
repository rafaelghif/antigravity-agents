---
id: issue-248
title: "docs: update context_map.md command documentation for new DX features"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
Ensure the agent's documentation maps the new developer experience (DX) commands and flags correctly in `context_map.md`.

## Tasks
- [x] Update `context_map.md` with descriptions of new options: `-q` for bootstrap/validate, `-i` for commit, `--clear-all`/`--prune` for lock. <!-- id: task-doc-update -->
- [x] Document `pause` and `resume` CLI commands. <!-- id: task-pause-resume-doc -->
- [x] Add missing `token` command documentation. <!-- id: task-token-doc -->

## Acceptance Criteria
- [x] Documentation accurately reflects the codebase features. <!-- id: criteria-doc-accuracy -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] `.agents/docs/context_map.md` <!-- id: audit-target-files -->
- Active module locks:
  - [x] None <!-- id: lock-none -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
