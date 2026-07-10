---
id: issue-239
title: "chore: implement MCP registry version upgrade and remaining audit hardening"
status: closed
assignee: rafaelghif
created_at: 2026-07-10
---

# Issue Details

## Problem Statement
chore: implement MCP registry version upgrade and remaining audit hardening

## Tasks
- [x] Propose design and module setup <!-- id: task-design -->
- [x] Lock required modules <!-- id: task-lock-modules -->
- [x] Update MCP server name to aac-v3-tools in mcp_server.py and configurations <!-- id: task-mcp-upgrade -->
- [x] Run test suite and check validation compliance <!-- id: task-verify-and-test -->

## Acceptance Criteria
- [x] Design proposal is recorded <!-- id: criteria-design-done -->
- [x] MCP name registers under aac-v3-tools <!-- id: criteria-mcp-updated -->
- [x] Workspace validation checks pass successfully <!-- id: criteria-validation-passes -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/scripts/mcp_server.py <!-- id: audit-target-files -->
  - [x] .agents/mcp_config.json <!-- id: audit-target-files-2 -->
  - [x] .agents/issues/issue_239.md <!-- id: audit-target-files-3 -->
- Active module locks:
  - [x] bootstrap <!-- id: lock-bootstrap -->
  - [x] .agents/scripts/mcp_server <!-- id: lock-mcp_server -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
