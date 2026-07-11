---
id: issue-282
title: "chore: audit MCP configurations and test active server tools"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
chore: audit MCP configurations and test active server tools

## Tasks
- [x] Audit mcp_config.json configurations and copy template files if missing <!-- id: task-audit-mcp-config -->
- [x] Test execution of aac-v3-tools and gitea MCP server tools <!-- id: task-test-mcp-tools -->

## Acceptance Criteria
- [x] MCP configurations are verified and compliant <!-- id: criteria-mcp-compliant -->
- [x] Active MCP server tools execute successfully <!-- id: criteria-mcp-tools-tested -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/mcp_config.json <!-- id: audit-target-files -->
- Active module locks:
  - [ ] .agents/mcp_config.json <!-- id: lock-mcp_config_json -->
  - [ ] .agents/scripts/cli/commands/bootstrap <!-- id: lock-bootstrap -->
  - [ ] .agents/tests/test_bootstrap <!-- id: lock-test_bootstrap -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
