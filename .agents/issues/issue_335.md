---
id: 335
title: "feat: enable local github mcp by default and document local gitea host"
status: open
assignee: rafaelghif
created_at: 2026-07-15
---

# Issue Details

## Problem Statement
feat: enable local github mcp by default and document local gitea host

## Tasks
- [x] Enable local Docker GitHub MCP server by default and disable Copilot remote server <!-- id: task-enable-local-github -->
- [x] Update github-mcp skill to prioritize local GitHub platform operations <!-- id: task-update-github-skill -->
- [x] Update gitea-mcp skill to clarify local instance host requirement <!-- id: task-update-gitea-skill -->

## Acceptance Criteria
- [x] github local server is enabled and Copilot remote is disabled in mcp_config.json <!-- id: ac-mcp-github-default -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/mcp_config.json <!-- id: target-mcp-config -->
  - [x] .agents/templates/mcp_config.json.template <!-- id: target-mcp-template -->
  - [x] .agents/skills/github-mcp/SKILL.md <!-- id: target-github-skill -->
  - [x] .agents/skills/gitea-mcp/SKILL.md <!-- id: target-gitea-skill -->
- Active module locks:
  - [x] None <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
