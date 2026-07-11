---
id: issue-283
title: "refactor: rename git_token to git_pat for clarity and standardization"
status: closed
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
refactor: rename git_token to git_pat for clarity and standardization

## Tasks
- [x] Rename git_token to git_pat inside git_profiles.json and git_profiles.example <!-- id: task-rename-profile-files -->
- [x] Refactor profile.py, dashboard.py, app.js, and git_api.py to use git_pat <!-- id: task-refactor-source-files -->
- [x] Update unit tests in test_profile.py and test_sync.py <!-- id: task-update-unit-tests -->
- [x] Update documentation references in README.md <!-- id: task-update-docs -->

## Acceptance Criteria
- [x] All references renamed from git_token to git_pat <!-- id: criteria-renamed -->
- [x] All unit tests pass successfully <!-- id: criteria-tests-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/git_profiles.json, .agents/git_profiles.example, .agents/dashboard/app.js, .agents/scripts/cli/commands/dashboard.py, .agents/scripts/cli/commands/profile.py, .agents/scripts/git_api.py, .agents/tests/test_profile.py, .agents/tests/test_sync.py, README.md <!-- id: audit-target-files -->
- Active module locks:
  - [ ] .agents/git_profiles.json, <!-- id: lock-git_profiles_json, -->
  - [ ] README.md <!-- id: lock-README_md -->
  - [ ] .agents/dashboard/app <!-- id: lock-app -->
  - [ ] .agents/scripts/cli/commands/bootstrap <!-- id: lock-bootstrap -->
  - [ ] .agents/scripts/cli/commands/dashboard <!-- id: lock-dashboard -->
  - [ ] .agents/scripts/cli/commands/profile <!-- id: lock-profile -->
  - [ ] .agents/scripts/git_api <!-- id: lock-git_api -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
