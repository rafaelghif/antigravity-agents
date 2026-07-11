---
id: issue-272
title: "integrate gitea mcp server configuration into workspace"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
Integrate Gitea MCP server configuration into workspace mcp_config.json to support company local Gitea instance integrations.

## Tasks
- [x] Append Gitea Docker-based MCP server and input parameters to `.agents/mcp_config.json` <!-- id: task-append-gitea-mcp -->
- [x] Verify validations pass and commit changes <!-- id: task-verify-gitea-finish -->

## Acceptance Criteria
- [x] `.agents/mcp_config.json` contains gitea configuration with access token and host parameters <!-- id: criteria-gitea-configured -->
- [x] Workspace passes all validation audits cleanly <!-- id: criteria-gitea-valid -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/mcp_config.json <!-- id: audit-target-files -->
- Active module locks:
  - [ ] None <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
