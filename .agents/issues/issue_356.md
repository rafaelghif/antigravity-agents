---
id: issue-356
title: "harden local mcp server jsonrpc and path checks"
status: closed
assignee: rafaelghif
created_at: 2026-07-16
---

# Issue Details

## Problem Statement
harden local mcp server jsonrpc and path checks

## Pre-Implementation Impact Analysis
- **Option A (Recommended)**: Harden JSON-RPC notification compliance, input parameter checks for tools (limiting task IDs and locks to safe alphanumeric/non-traversal names), and strictly check import paths under target script dirs.
- **Option B**: Skip input parameter checks, risking traversals or untrusted execution.

## Tasks
- [x] Task 1: Harden dynamic imports and workspace validation check in `mcp_server.py`. <!-- id: task-harden-imports -->
- [x] Task 2: Implement JSON-RPC notification handler to prevent replying to notification requests in `mcp_server.py`. <!-- id: task-harden-notifications -->
- [x] Task 3: Sanitize input parameters in tool execution blocks inside `mcp_server.py`. <!-- id: task-sanitize-inputs -->
- [x] Task 4: Add comprehensive tests for the hardened logic in `test_mcp_server.py`. <!-- id: task-tests -->
- [x] Task 5: Run validation guard to verify all checks pass. <!-- id: task-validate -->

## Acceptance Criteria
- [x] Unhandled notifications do not receive JSON-RPC error responses (returns None). <!-- id: ac-notifications -->
- [x] All 279 tests and validation guard passes successfully. <!-- id: ac-tests-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] `.agents/scripts/mcp_server.py` <!-- id: target-mcp-server -->
  - [x] `.agents/tests/test_mcp_server.py` <!-- id: target-test-mcp-server -->
- Active module locks:
  - [ ] None <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
