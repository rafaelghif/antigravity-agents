---
id: issue-8
title: "Patch Critical Secret Leaks and Workflow Crash Loops in Bootstrapper"
status: open
assignee: agent-antigravity
milestone: "v3.133"
created_at: 2026-07-17
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Markdown / Python CLI
- **Architecture**: Secret Isolation & Workflow Stability

## Tasks
- [x] Add `.agents/mcp_config.json` to `.gitignore.template` to prevent API token leaks <!-- id: task-1 -->
- [x] Add `.agents/mcp_config.json` to `.antigravityignore.template` <!-- id: task-2 -->
- [x] Inject `git init` fallback into `bootstrap.py` so that agents don't crash on `epic/task` branch checks when AAC is initialized in a fresh empty folder <!-- id: task-3 -->
- [ ] Push changes to git <!-- id: task-4 -->

## Acceptance Criteria
- [ ] MCP configuration secrets are safely ignored by git and agent scans <!-- id: ac-1 -->
- [ ] Fresh installs do not break the Epic/Task workflow due to missing git initialization <!-- id: ac-2 -->

## Rule & Schema Compliance Audit
- [x] Zero-Trust & Security rule strictly enforced <!-- id: audit-1 -->
