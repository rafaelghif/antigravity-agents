---
id: issue-306
title: "Initialize and bootstrap config.json template and fix global copy installer issues"
status: closed
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
We need to introduce a workspace setting file `.agents/config.json` default configuration and template to enable the workflow mode overrides (e.g. solo vs team mode). This file and its template mapping should be added to prevent missing configurations during target installations/bootstrapping, and the installer must be updated to exclude overwriting it.

## Tasks
- [x] Create config.json.template under .agents/templates <!-- id: task-create-template -->
- [x] Add config.json template mapping to .agents/docs/template_map.md <!-- id: task-update-map -->
- [x] Update bootstrap.py to generate config.json from template during bootstrap <!-- id: task-update-bootstrap -->
- [x] Update install.py to exclude config.json from recursive copying <!-- id: task-update-install -->
- [x] Add unit tests in test_bootstrap.py verifying config.json generation <!-- id: task-unit-tests -->
- [x] Run validation tests and verify workspace compliance <!-- id: task-run-validation -->

## Acceptance Criteria
- [x] `.agents/templates/config.json.template` exists and defines the default `"workflow_mode": "team"`. <!-- id: ac-template-exists -->
- [x] `template_map.md` maps `.agents/templates/config.json.template` to `.agents/config.json`. <!-- id: ac-map-updated -->
- [x] `bootstrap.py` automatically generates `.agents/config.json` from the template if it does not exist. <!-- id: ac-bootstrap-generates -->
- [x] `install.py` excludes `.agents/config.json` from installation copying to avoid overwriting user settings. <!-- id: ac-install-excludes -->
- [x] All unit tests pass cleanly. <!-- id: ac-tests-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/tasks/board.md <!-- id: audit-target-board -->
  - [x] .agents/docs/template_map.md <!-- id: audit-target-map -->
  - [x] .agents/scripts/cli/commands/bootstrap.py <!-- id: audit-target-bootstrap -->
  - [x] .agents/scripts/cli/commands/install.py <!-- id: audit-target-install -->
  - [x] .agents/tests/test_bootstrap.py <!-- id: audit-target-tests -->
  - [x] .agents/issues/issue_306.md <!-- id: audit-target-issue -->
- Active module locks:
  - [x] .agents/scripts/cli/commands/bootstrap <!-- id: lock-bootstrap -->
  - [x] .agents/scripts/cli/commands/install <!-- id: lock-install -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
