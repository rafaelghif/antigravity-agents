---
id: issue-298
title: "Fix Global Folder Directory Couplings"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
Fix global directory coupling issues by introducing AAC_HOME/AAC_SSH_DIR env overrides and refining validation exclusions.

## Tasks
- [x] Add AAC_HOME env var support in token.py <!-- id: task-token-env -->
- [x] Add AAC_SSH_DIR env var support in profile.py <!-- id: task-profile-env -->
- [x] Update validate.py to exclude false positive warnings on dashboard/profile/benchmarks <!-- id: task-validate-exclude -->
- [x] Run validation tests and verify code compliance <!-- id: task-run-validation -->

## Acceptance Criteria
- [x] Global folder couplings warning messages are eliminated in validate check. <!-- id: ac-no-warnings -->
- [x] Active token transcript files path resolves relative to AAC_HOME when configured. <!-- id: ac-env-resolves -->
- [x] Validation checks pass cleanly. <!-- id: ac-validation -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/scripts/validate.py <!-- id: audit-target-files -->
  - [x] .agents/scripts/cli/commands/token.py <!-- id: audit-target-files-2 -->
  - [x] .agents/scripts/cli/commands/profile.py <!-- id: audit-target-files-3 -->
- Active module locks:
  - [ ] validate <!-- id: lock-validate -->
  - [ ] cli/commands/token <!-- id: lock-token -->
  - [ ] cli/commands/profile <!-- id: lock-profile -->
  - [ ] .agents/scripts/cli/commands/token <!-- id: lock-token -->
  - [ ] .agents/scripts/cli/commands/profile <!-- id: lock-profile -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
