---
id: issue-315
title: "feat(upgrade): prioritize local templates in bootstrap and add blueprints and workflows to auto-upgrade paths"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
When running local installation audits (e.g., via `install.py`), templates are copied to `.agents/templates/` first. However, `bootstrap.py` always attempts to fetch from the remote Git repository (`https://github.com/rafaelghif/antigravity-agents.git`) rather than reading the local `.agents/templates/` folder, causing local/branch template edits to be ignored during installation audits. Furthermore, the `upgrade.py` command does not list `.agents/blueprints/` and `.agents/workflows/` in the upgraded paths list, leaving them stale during framework updates.

## Tasks
- [x] Move issue-315 to Doing in task board <!-- id: task-move-board -->
- [x] Update bootstrap.py to check for and prioritize local templates at local_src_root first <!-- id: task-update-bootstrap -->
- [x] Update upgrade.py to add blueprints and workflows folders to core paths upgrade lists <!-- id: task-update-upgrade -->
- [x] Run validation tests and verify workspace compliance <!-- id: task-run-validation -->

## Acceptance Criteria
- [x] `bootstrap.py` prioritizes local offline templates if `.agents/templates/` is present at `local_src_root`. <!-- id: ac-local-prioritized -->
- [x] `upgrade.py` correctly updates `.agents/blueprints/` and `.agents/workflows/` when executing upgrades. <!-- id: ac-upgrade-folders-included -->
- [x] All unit tests and workspace validations pass cleanly. <!-- id: ac-tests-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/tasks/board.md <!-- id: audit-target-board -->
  - [x] .agents/scripts/cli/commands/bootstrap.py <!-- id: audit-target-bootstrap -->
  - [x] .agents/scripts/cli/commands/upgrade.py <!-- id: audit-target-upgrade -->
  - [x] .agents/issues/issue_315.md <!-- id: audit-target-issue -->
- Active module locks:
  - [x] .agents/scripts/cli/commands/bootstrap <!-- id: lock-bootstrap -->
  - [x] .agents/scripts/cli/commands/upgrade <!-- id: lock-upgrade -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
