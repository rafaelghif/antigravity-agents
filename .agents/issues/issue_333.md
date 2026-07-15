---
id: 333
title: "feat: adjust mcp config templates and create github/gitea mcp skills"
status: closed
assignee: rafaelghif
created_at: 2026-07-15
---

# Issue Details

## Problem Statement
feat: adjust mcp config templates and create github/gitea mcp skills

## Tasks
- [x] Adjust mcp_config.json and its template to include both remote and local GitHub configuration <!-- id: task-adjust-mcp -->
- [x] Create the github-mcp workspace skill playbook <!-- id: task-github-skill-create -->
- [x] Create the gitea-mcp workspace skill playbook <!-- id: task-gitea-skill-create -->

## Acceptance Criteria
- [x] Workspace skills registry contains github-mcp and gitea-mcp skills <!-- id: ac-skills-registered -->

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
