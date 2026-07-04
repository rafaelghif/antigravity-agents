---
id: issue-170
title: "Implement zero-dependency MCP server and registration command"
status: open
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
Implement zero-dependency MCP server and registration command

## Tasks
- [x] Update `.agents/issues/issue_167.md` subtasks and claim in board
- [x] Create zero-dependency standard stdin/stdout JSON-RPC MCP server `mcp_server.py`
- [x] Register `mcp` command in `helper.py` to support `register` and `start` subcommands
- [x] Document the MCP setup and configuration in `README.md`
- [x] Run validation checks and close issue

## Acceptance Criteria
- [x] `mcp_server.py` handles JSON-RPC initialization, listing, and tool calls correctly
- [x] Running `./helper.sh mcp register` successfully adds the server to Cline's configuration file
- [x] Unit tests and validation pass successfully
