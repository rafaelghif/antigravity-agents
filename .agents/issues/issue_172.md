---
id: issue-172
title: "Improve MCP path portability and automate registration in bootstrap"
status: open
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
Improve MCP path portability and automate registration in bootstrap

## Tasks
- [x] Update `.agents/issues/issue_172.md` subtasks and claim in board
- [x] Use relative paths for `.agents/mcp_config.json` configuration
- [x] Trigger MCP registration automatically inside `bootstrap.py`
- [x] Run validation checks and close issue

## Acceptance Criteria
- [x] `.agents/mcp_config.json` uses a portable relative path (`.agents/scripts/mcp_server.py`)
- [x] `./helper.sh bootstrap` automatically runs MCP registration successfully
- [x] All unit tests pass successfully
