---
id: issue-284
title: "Fix MCP config bootstrapping registration and template drift issues"
status: closed
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
The MCP configuration (`.agents/mcp_config.json`) is currently copied as a static helper file during bootstrapping. This introduces multiple critical issues:
1. Running bootstrap with `--force` or during updates overrides the file entirely, destroying customized user settings (like Gitea and GitHub credentials).
2. During bootstrapping, importing `mcp_server.py` from the temporary repository clone to run `register_server()` registers the server relative to the temporary source path rather than the target workspace. This results in the registered path being lost when the temporary folder is deleted, leaving the target workspace with an unmodified static `mcp_config.json` that contains hardcoded platform-drifted commands (e.g. `python3` instead of `python` on Windows).

## Tasks
- [x] Relocate `.agents/mcp_config.json` to `.agents/templates/mcp_config.json.template` <!-- id: task-relocate -->
- [x] Update `bootstrap.py` to remove `mcp_config.json` from the helpers list, read it from the templates if missing, and import `mcp_server.py` from the target workspace to register it properly <!-- id: task-update-bootstrap -->
- [x] Verify test suite and run code validation <!-- id: task-validate -->

## Acceptance Criteria
- [x] `.agents/mcp_config.json` is not overwritten on forced bootstrap/update if it already exists. <!-- id: ac-no-overwrite -->
- [x] Bootstrapping registers `aac-v3-tools` relative to the target workspace rather than the temp directory. <!-- id: ac-register-rel -->
- [x] Unit tests pass successfully. <!-- id: ac-tests-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/scripts/cli/commands/bootstrap.py <!-- id: audit-target-files -->
- Active module locks:
  - [ ] .agents/scripts/cli/commands/bootstrap <!-- id: lock-bootstrap -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
