---
id: issue-295
title: "Fix weaknesses in framework release warning and commit amending"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
We need to address the two weaknesses identified in our audit report:
1. Handle HTTP 401/403 errors gracefully with a `[WARN]` message instead of a raw traceback `[FAIL]` when creating a GitHub release draft.
2. Bypass the branch prefix enforcer when running inside Git commit hooks (so developers can amend or commit intermediate work freely).

## Tasks
- [x] Catch HTTP 401/403 errors in `git_api.py` release creation <!-- id: task-graceful-auth-errors -->
- [x] Bypass branch prefix enforcer during Git hooks in `validate.py` <!-- id: task-bypass-prefix-hooks -->
- [x] Run validation tests and verify code compliance <!-- id: task-run-validation -->

## Acceptance Criteria
- [x] Authorization failures on remote release creation print `[WARN]` instead of `[FAIL]`. <!-- id: ac-graceful-errors -->
- [x] Branch prefix alignment is not enforced during Git hook execution. <!-- id: ac-bypass-hooks -->
- [x] Validation checks pass cleanly. <!-- id: ac-validation-passes -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/scripts/git_api.py <!-- id: audit-git-api -->
  - [x] .agents/scripts/validate.py <!-- id: audit-validate -->
- Active module locks:
  - [ ] .agents/scripts/git_api <!-- id: lock-git_api -->
  - [ ] validate <!-- id: lock-validate -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
