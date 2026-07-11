---
id: issue-301
title: "Fix Changelog Versioning and Issue Naming Skew"
status: closed
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
Fix versioning detection in bootstrap/changelog, exclude CHANGELOG.md from target installations, and prevent issue filename truncation for custom/task IDs.

## Tasks
- [x] Task 1: Exclude CHANGELOG.md from installation copy list inside install.py <!-- id: task-exclude-changelog -->
- [x] Task 2: Remove dummy 'test-proj' check in bootstrap.py and changelog.py to prevent version mismatches <!-- id: task-is-core-check -->
- [x] Task 3: Refactor get_issue_path in issue.py to preserve full suffix names for custom issues <!-- id: task-issue-suffix -->
- [x] Task 4: Run local unit tests and validation guard verification checks <!-- id: task-run-validation -->

## Acceptance Criteria
- [x] CHANGELOG.md is excluded from clean target installations. <!-- id: ac-exclude-changelog -->
- [x] Target projects initialize with correct version (e.g. 0.1.0) and do not jump to V3 agent core version. <!-- id: ac-version-correct -->
- [x] Custom issue files preserve full slug suffixes instead of truncating to the last word. <!-- id: ac-custom-issue-suffix -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/scripts/cli/commands/install.py <!-- id: audit-target-files -->
  - [x] .agents/scripts/cli/commands/bootstrap.py <!-- id: audit-target-files-2 -->
  - [x] .agents/scripts/cli/commands/changelog.py <!-- id: audit-target-files-3 -->
  - [x] .agents/scripts/cli/commands/issue.py <!-- id: audit-target-files-4 -->
- Active module locks:
  - [ ] .agents/scripts/cli/commands/install <!-- id: lock-install -->
  - [ ] .agents/scripts/cli/commands/bootstrap <!-- id: lock-bootstrap -->
  - [ ] .agents/scripts/cli/commands/changelog <!-- id: lock-changelog -->
  - [ ] .agents/scripts/cli/commands/issue <!-- id: lock-issue -->
  - [ ] .agents/tests/test_changelog <!-- id: lock-test_changelog -->
  - [ ] .agents/tests/test_issue <!-- id: lock-test_issue -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
