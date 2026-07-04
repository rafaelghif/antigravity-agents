---
id: issue-171
title: "Align MCP configuration with Google Antigravity specifications"
status: closed
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
Align MCP configuration with Google Antigravity specifications

## Tasks
- [x] Update `.agents/issues/issue_171.md` subtasks and claim in board
- [x] Modify `register_server()` in `mcp_server.py` to register in both `.agents/mcp_config.json` and `~/.gemini/config/mcp_config.json`
- [x] Add lock for `cli/commands/mcp` and test registrations
- [x] Run validation checks and close issue

## Acceptance Criteria
- [x] Running `./helper.sh mcp register` writes the correct configuration format to `.agents/mcp_config.json`
- [x] Running `./helper.sh mcp register` writes the correct configuration format to `~/.gemini/config/mcp_config.json`
- [x] All unit tests pass successfully
