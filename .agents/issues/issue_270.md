---
id: issue-270
title: "resolve codebase audit findings and implement template mapping documentation"
status: closed
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
Resolve critical security, architecture, and parity findings discovered in codebase audit (MCP server global registration leakage, rules duplicates) and create template-target mapping documentation to prevent platform-drift.

## Tasks
- [x] Fix global registry leaks in `mcp_server.py` and `commands/mcp.py` <!-- id: task-fix-mcp-registry -->
- [x] Standardize rules synthesized section to index 6 and cleanup `.agents/rules.md` duplicates <!-- id: task-fix-rules-sync -->
- [x] Create `template_map.md` mapping file and update `AGENTS.md` and `rules.md` read flows <!-- id: task-create-template-map -->
- [x] Verify unit tests and validations pass <!-- id: task-verify-findings-finish -->

## Acceptance Criteria
- [x] MCP server defaults to workspace-local registration and makes global config opt-in via `--global` flag <!-- id: criteria-mcp-isolated -->
- [x] `.agents/rules.md` synthesized rules section matches section 6 header with zero duplication <!-- id: criteria-rules-clean -->
- [x] `.agents/docs/template_map.md` is present and mandatory for agents to read before coding <!-- id: criteria-template-doc -->
- [x] All unit tests and workspace validations pass cleanly <!-- id: criteria-tests-valid -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/scripts/mcp_server.py <!-- id: audit-target-files -->
  - [x] .agents/scripts/cli/commands/mcp.py
  - [x] .agents/scripts/sync.py
  - [x] .agents/scripts/cli/commands/context.py
  - [x] .agents/scripts/cli/commands/dashboard.py
  - [x] .agents/rules.md
  - [x] .agents/templates/rules.md.template
  - [x] .agents/docs/template_map.md
  - [x] AGENTS.md
  - [x] .agents/tests/test_dashboard.py
  - [x] .agents/tests/test_sync.py
- Active module locks:
  - [ ] None <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
