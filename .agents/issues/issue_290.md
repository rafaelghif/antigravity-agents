---
id: issue-290
title: "Relocate mcp_config to .agents root folder and update bootstrap"
status: closed
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
The template `.agents/templates/mcp_config.json.template` should be relocated to `.agents/mcp_config.json` directly to prevent missing file errors during installation and ensure git-tracked online availability. We must update the bootstrap command to generate `.agents/mcp_config.json` from the root file if missing, and adjust the validation parity check.

## Tasks
- [x] Rename `.agents/templates/mcp_config.json.template` to `.agents/mcp_config.json` <!-- id: task-rename-mcp -->
- [x] Update `bootstrap.py` to exclude `mcp_config.json` from recursive copies and copy from root config if missing <!-- id: task-update-bootstrap -->
- [x] Update `template_map.md` and the parity check in `validate.py` <!-- id: task-update-validate-map -->
- [x] Run validation tests and verify code compliance <!-- id: task-run-tests -->

## Acceptance Criteria
- [x] `.agents/mcp_config.json` exists in the `.agents` root. <!-- id: ac-mcp-exists -->
- [x] Bootstrap command successfully generates `.agents/mcp_config.json` when missing. <!-- id: ac-bootstrap-generates -->
- [x] Unit tests pass successfully. <!-- id: ac-tests-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/scripts/cli/commands/bootstrap.py <!-- id: audit-bootstrap-file -->
  - [x] .agents/docs/template_map.md <!-- id: audit-map-file -->
  - [x] .agents/scripts/validate.py <!-- id: audit-validate-file -->
- Active module locks:
  - [ ] .agents/scripts/validate <!-- id: lock-validate -->
  - [ ] .agents/scripts/cli/commands/bootstrap <!-- id: lock-bootstrap -->
  - [ ] .agents/docs/template_map.md <!-- id: lock-template_map_md -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
