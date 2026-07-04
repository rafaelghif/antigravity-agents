---
id: issue-196
title: "Make MCP server dynamically resolve target project scripts directory"
status: open
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
When a target project calls tools via the globally registered MCP server (`aac-v2-tools`), the server imports and executes CLI command scripts (`validate.py`, `token.py`, `lock.py`) from the core agent's repository path instead of the target project's own `.agents/scripts` directory. This bypasses target project customization (e.g. customized validation rules).

## Tasks
- [x] Implement dynamic CWD-based scripts resolution in `mcp_server.py`. <!-- id: subtask-cwd-resolution -->
- [x] Run validation suite and ensure unit tests pass. <!-- id: subtask-validation -->

## Acceptance Criteria
- [x] The MCP server dynamically resolves the path to `cli/commands/token.py`, `cli/commands/lock.py`, and `validate.py` under `os.getcwd()/.agents/scripts/` if that directory exists.
- [x] If the workspace is not bootstrapped, it falls back to the globally registered script's physical location.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [.agents/scripts/mcp_server.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/mcp_server.py)
- Active module locks:
  - `mcp` (locked on branch `feat/issue-196`) <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
