---
id: 332
title: "feat: integrate github and gitea mcp settings into git profiles"
status: open
assignee: rafaelghif
created_at: 2026-07-15
---

# Issue Details

## Problem Statement
feat: integrate github and gitea mcp settings into git profiles

## Tasks
- [x] Add GitHub MCP settings to profile template and configuration <!-- id: task-github-mcp -->
- [x] Add Gitea MCP settings to profile template and configuration <!-- id: task-gitea-mcp -->

## Acceptance Criteria
- [x] Git profiles template includes GitHub and Gitea MCP credentials keys <!-- id: ac-profiles-keys -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/git_profiles.example <!-- id: target-git-profiles-example -->
- Active module locks:
  - [x] None <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
