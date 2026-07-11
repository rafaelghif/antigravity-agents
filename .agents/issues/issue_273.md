---
id: issue-273
title: "enhance readme with comprehensive onboarding and setup details"
status: closed
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
Enhance README.md to add detailed developer setup instructions (Git profiles commands, monorepos path configs, MCP server integration parameters).

## Tasks
- [x] Update `README.md` to add Git profiles configuration commands <!-- id: task-readme-profiles -->
- [x] Add Monorepos and Gitea/GitHub MCP server setups to `README.md` <!-- id: task-readme-monorepo-mcp -->
- [x] Verify validations pass cleanly <!-- id: task-readme-verify -->

## Acceptance Criteria
- [x] `README.md` details developer profiles rotation setup and CLI commands <!-- id: criteria-readme-profiles-documented -->
- [x] `README.md` documents Gitea local and GitHub remote MCP config parameters <!-- id: criteria-readme-mcp-documented -->
- [x] All unit tests and validations pass cleanly <!-- id: criteria-readme-valid -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] README.md <!-- id: audit-target-files -->
- Active module locks:
  - [ ] None <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
