---
id: issue-285
title: "Map mcp_config in template_map.md and enforce programmatical template parity checks"
status: closed
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
To prevent configuration and template drift across target projects:
1. `.agents/templates/mcp_config.json.template` should be documented and mapped inside `.agents/docs/template_map.md`.
2. Implement a programmatic template parity check in the validation guard (`validate.py`) to verify that if any target workspace configuration file is modified, its corresponding source template is also updated to keep them synchronized.

## Tasks
- [x] Add `.agents/templates/mcp_config.json.template` -> `.agents/mcp_config.json` mapping to `.agents/docs/template_map.md` <!-- id: task-update-map -->
- [x] Implement template parity check in `.agents/scripts/validate.py` inside `audit_workspace_sync()` <!-- id: task-update-validate -->
- [x] Run validation tests and verify code compliance <!-- id: task-run-tests -->

## Acceptance Criteria
- [x] `template_map.md` lists `.agents/mcp_config.json` target file. <!-- id: ac-map-listed -->
- [x] Validation guard prints a warning if a target file is modified but its template is not. <!-- id: ac-warning-printed -->
- [x] Unit tests pass successfully. <!-- id: ac-tests-passed -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/docs/template_map.md <!-- id: audit-target-files -->
  - [x] .agents/scripts/validate.py <!-- id: audit-validate-file -->
- Active module locks:
  - [ ] .agents/scripts/validate <!-- id: lock-validate -->
  - [ ] .agents/docs/template_map.md <!-- id: lock-template_map_md -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
