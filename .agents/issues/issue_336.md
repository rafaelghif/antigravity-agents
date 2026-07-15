---
id: 336
title: "feat: remove github copilot mcp reference and configs"
status: open
assignee: rafaelghif
created_at: 2026-07-15
---

# Issue Details

## Problem Statement
feat: remove github copilot mcp reference and configs

## Tasks
- [x] Delete github-copilot server entry from mcp_config.json and mcp_config.json.template <!-- id: task-remove-copilot-config -->
- [x] Remove remote GitHub Copilot sections and references from the github-mcp skill playbook <!-- id: task-remove-copilot-skill -->

## Acceptance Criteria
- [x] github-copilot server entry is completely removed from configuration and template <!-- id: ac-copilot-removed -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/mcp_config.json <!-- id: target-mcp-config -->
  - [x] .agents/templates/mcp_config.json.template <!-- id: target-mcp-template -->
  - [x] .agents/skills/github-mcp/SKILL.md <!-- id: target-github-skill -->
- Active module locks:
  - [x] None <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
