---
id: issue-312
title: "Fix installer config file overwriting and correct template map verify.yml workflow path"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
The installer (`install.py`) recursively copies all root repository files without excluding target project-specific files such as `.gitignore`, `.antigravityignore`, `Dockerfile`, and `README.md`. This causes the target project's custom versions of these files to be silently overwritten during installation/upgrades. Additionally, there is a path mismatch in `template_map.md` which refers to `.github/workflows/ci.yml` instead of the actual generated file `.github/workflows/verify.yml`.

## Tasks
- [x] Move issue-312 to Doing in task board <!-- id: task-move-board -->
- [x] Lock install and test_install modules <!-- id: task-lock-modules -->
- [x] Exclude .gitignore, .antigravityignore, Dockerfile, and README.md in install.py <!-- id: task-exclude-files -->
- [x] Update test_install.py unit tests to match new exclusions <!-- id: task-update-tests -->
- [x] Fix template_map.md workflow file path reference <!-- id: task-fix-docs -->
- [x] Run validation tests and verify workspace compliance <!-- id: task-run-validation -->

## Acceptance Criteria
- [x] `.gitignore`, `.antigravityignore`, `Dockerfile`, and `README.md` are excluded by `should_exclude()` in `install.py`. <!-- id: ac-install-exclusions -->
- [x] `test_install.py` asserts that `Dockerfile` is excluded, and all unit tests pass cleanly. <!-- id: ac-tests-pass -->
- [x] `.agents/docs/template_map.md` correctly lists the target for `ci_github_workflow.yml.template` as `.github/workflows/verify.yml`. <!-- id: ac-docs-verify -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/tasks/board.md <!-- id: audit-target-board -->
  - [x] .agents/scripts/cli/commands/install.py <!-- id: audit-target-install -->
  - [x] .agents/tests/test_install.py <!-- id: audit-target-test-install -->
  - [x] .agents/docs/template_map.md <!-- id: audit-target-docs -->
  - [x] .agents/issues/issue_312.md <!-- id: audit-target-issue -->
- Active module locks:
  - [x] .agents/scripts/cli/commands/install <!-- id: lock-install -->
  - [x] .agents/tests/test_install <!-- id: lock-test_install -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
