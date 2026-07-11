---
id: issue-271
title: "integrate github mcp server config and update template parity mappings"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
Integrate GitHub API MCP server configuration into workspace mcp_config.json and extend template_map.md with missing config examples and package template mappings.

## Tasks
- [x] Append github http mcp server to `.agents/mcp_config.json` <!-- id: task-append-github-mcp -->
- [x] Add `.agents/git_profiles.example`, `.agents/projects.example`, and package templates to `template_map.md` <!-- id: task-extend-template-map -->
- [x] Verify validations pass and record lessons learned <!-- id: task-verify-mcp-git-finish -->

## Acceptance Criteria
- [x] `.agents/mcp_config.json` contains github and aac-v3-tools mcp servers <!-- id: criteria-mcp-server-present -->
- [x] `.agents/docs/template_map.md` includes git_profiles, projects, and package templates <!-- id: criteria-template-mapped -->
- [x] All validations pass cleanly <!-- id: criteria-all-passed -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/mcp_config.json <!-- id: audit-target-files -->
  - [x] .agents/docs/template_map.md
- Active module locks:
  - [ ] None <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
