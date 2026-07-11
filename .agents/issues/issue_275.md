---
id: issue-275
title: "feat: secure profile command against shell command injections and mcp server workspace coupling"
status: closed
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
feat: secure profile command against shell command injections and mcp server workspace coupling

## Tasks
- [x] Add validate_safe_path to profile.py and prevent command injections <!-- id: task-secure-profile -->
- [x] Add unit tests for safe path validation to test_profile.py <!-- id: task-test-profile -->
- [x] Harden mcp_server.py against global workspace coupling <!-- id: task-secure-mcp -->
- [x] Add unit tests for workspace isolation to test_mcp.py <!-- id: task-test-mcp -->
- [x] Add print_err and local fallback check to bootstrap.py <!-- id: task-secure-bootstrap -->
- [x] Add unit tests for bootstrap local fallback to test_bootstrap.py <!-- id: task-test-bootstrap -->

## Acceptance Criteria
- [x] Validation guard passes without module lock or branch errors <!-- id: criteria-validation-pass -->
- [x] profile, mcp, bootstrap unit tests pass successfully <!-- id: criteria-tests-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/scripts/cli/commands/profile.py, .agents/tests/test_profile.py, .agents/scripts/mcp_server.py, .agents/tests/test_mcp.py, .agents/scripts/cli/commands/bootstrap.py, .agents/tests/test_bootstrap.py <!-- id: audit-target-files -->
- Active module locks:
  - [ ] .agents/scripts/cli/commands/profile <!-- id: lock-profile -->
  - [ ] .agents/scripts/cli/commands/bootstrap <!-- id: lock-bootstrap -->
  - [ ] .agents/scripts/mcp_server <!-- id: lock-mcp_server -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
