---
id: issue-227
title: "Implement V4 Phase 1: Git Cleanliness & Metadata Isolation"
status: closed
assignee: corporate-work
created_at: 2026-07-09
---

# Issue Details

## Problem Statement
Implement V4 Phase 1: Git Cleanliness & Metadata Isolation

## Tasks
- [x] Define `.agents/state/` directory and append to `.gitignore` and `.antigravityignore` <!-- id: task-state-ignore -->
- [x] Relocate and update references to `active_context.md` to `.agents/state/active_context.md` <!-- id: task-context-relocate -->
- [x] Relocate and update references to `locks.json` to `.agents/state/locks.json` <!-- id: task-locks-relocate -->
- [x] Relocate and update references to `token_budget.json` to `.agents/state/token_budget.json` <!-- id: task-budget-relocate -->
- [x] Relocate and update references to CLI and token logs to `.agents/state/logs/` <!-- id: task-logs-relocate -->
- [x] Update `sync_issues` in `issue.py` to prevent required task list commits and operate cleanly in git status <!-- id: task-sync-refactor -->
- [x] Run full validation suite and verify unit tests pass successfully <!-- id: task-validate-pass -->

## Acceptance Criteria
- [x] All transient metadata (locks, context, logs, local budget caches) are located under `.agents/state/` and ignored by Git status.
- [x] All 192 unit tests pass successfully with updated paths.


## Rule & Schema Compliance Audit
- Target files to edit:
  - [ ] None <!-- id: audit-target-files -->
- Active module locks:
  - [ ] None <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [ ] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [ ] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [ ] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
