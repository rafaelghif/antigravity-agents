---
id: issue-316
title: "feat(mcp): harden mcp server json-rpc compliance, path imports, and tool execution error capturing"
status: closed
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
The MCP server `mcp_server.py` lacks robust error handling for standard JSON-RPC errors, potentially crashing or failing silently on malformed requests. Furthermore, it does not append target workspace directory paths to `sys.path`, creating risks of import errors when loaded dynamic commands import local script dependencies. Finally, it only redirects stdout and lets stderr write to the raw console (which can corrupt the JSON-RPC stdout stream on some hosts) and lacks robust unhandled exception wrapping for tool execution.

## Tasks
- [x] Move issue-316 to Doing in task board <!-- id: task-move-board -->
- [x] Add sys.path dynamic resolution for target scripts directory in mcp_server.py <!-- id: task-update-sys-path -->
- [x] Harden call_tool() in mcp_server.py to redirect both stdout/stderr and catch unhandled exceptions <!-- id: task-update-capture -->
- [x] Implement proper JSON-RPC error responses in handle_message() / start_server() <!-- id: task-update-jsonrpc -->
- [x] Create unit tests for MCP server protocol handling in .agents/tests/ <!-- id: task-create-tests -->
- [x] Run validation tests and verify workspace compliance <!-- id: task-run-validation -->

## Acceptance Criteria
- [x] `sys.path` contains the target scripts directory so dynamic commands import helper modules cleanly. <!-- id: ac-sys-path-resolved -->
- [x] Tool execution captures both stdout and stderr, returning stderr output inside the tool response instead of leaking. <!-- id: ac-stderr-captured -->
- [x] Unhandled exceptions in `call_tool()` are caught and returned as structured errors. <!-- id: ac-exceptions-handled -->
- [x] Parse errors or malformed JSON-RPC messages return compliant JSON-RPC error payloads (e.g. code `-32700`, `-32600`). <!-- id: ac-rpc-compliant -->
- [x] New unit tests verify correct JSON-RPC outputs and error payloads. <!-- id: ac-tests-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/tasks/board.md <!-- id: audit-target-board -->
  - [x] .agents/scripts/mcp_server.py <!-- id: audit-target-mcp -->
  - [x] .agents/tests/test_mcp_server.py <!-- id: audit-target-test-mcp -->
  - [x] .agents/issues/issue_316.md <!-- id: audit-target-issue -->
- Active module locks:
  - [ ] mcp <!-- id: lock-mcp -->
  - [ ] .agents/scripts/mcp_server <!-- id: lock-mcp_server -->
  - [ ] mcp_server <!-- id: lock-mcp_server -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
