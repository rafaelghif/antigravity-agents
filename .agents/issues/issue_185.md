---
id: issue-185
title: "Fix audit vulnerabilities and bugs"
status: open
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
Fix audit vulnerabilities and bugs

## Tasks
- [x] Fix local web dashboard CSRF in dashboard.py <!-- id: task-csrf -->
- [x] Fix background auto-upgrade daemon thread in helper.py and upgrade.py <!-- id: task-upgrade-thread -->
- [ ] Fix ADR sync regex in sync.py <!-- id: task-sync-regex -->
- [ ] Fix git hook prefix path bug in bootstrap.sh <!-- id: task-hook-prefix -->
- [ ] Fix Windows MCP Python command in mcp_server.py <!-- id: task-mcp-windows -->
- [ ] Fix test suite mock safety compliance for sys.exit in test files <!-- id: task-test-compliance -->

## Acceptance Criteria
- [x] All 10 validation audits pass
- [x] All unit tests pass successfully

