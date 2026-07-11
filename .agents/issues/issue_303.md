---
id: issue-303
title: "Fix changelog classification bugs"
status: closed
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
Changelog parsing incorrectly classifies bug fix tasks as features if they are committed under a feat/ branch prefix or with a feat: conventional commit prefix. The classifier must prioritize local issue metadata parsing (checking fix before feat keywords) to ensure correct SemVer bumps.

## Tasks
- [x] Task 1: Refactor classify_from_local_issue in changelog.py to evaluate fix keywords before feat keywords. <!-- id: task-reorder-keywords -->
- [x] Task 2: Refactor parse_conventional_commits in changelog.py to override conventional commit types with local issue classification if present. <!-- id: task-override-cat -->
- [x] Task 3: Add unit tests in test_changelog.py verifying the priority classification overrides. <!-- id: task-add-tests -->
- [x] Task 4: Run validation checks and merge. <!-- id: task-run-validation -->

## Acceptance Criteria
- [x] classify_from_local_issue correctly classifies issues with "Add fix for ..." as fixes. <!-- id: ac-reorder-keywords -->
- [x] parse_conventional_commits overrides ctype with local issue category. <!-- id: ac-override-cat -->
- [x] Validation suite passes successfully. <!-- id: ac-validation-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/scripts/cli/commands/changelog.py <!-- id: audit-target-files -->
  - [x] .agents/tests/test_changelog.py <!-- id: audit-target-files-2 -->
- Active module locks:
  - [ ] .agents/tests/test_changelog <!-- id: lock-test_changelog -->
  - [ ] changelog <!-- id: lock-changelog -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
