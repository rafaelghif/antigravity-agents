---
id: issue-215
title: "Harden agent workspace, upgrade logic, base merge checks, and MCP isolation"
status: open
assignee: agent-antigravity
created_at: 2026-07-09
---

# Issue Details

## Problem Statement
Harden agent workspace, upgrade logic, base merge checks, and MCP isolation

## Tasks
- [x] Implement MCP workspace-isolation verification in mcp_server.py <!-- id: task-mcp-isolation -->
- [x] Add backup logic and status warnings in upgrade.py to prevent destructive upgrades <!-- id: task-upgrade-backup -->
- [x] Implement auto-rollback and dirty status check in issue close action inside issue.py <!-- id: task-merge-rollback -->
- [x] Implement local offline fallback template copying in bootstrap.py <!-- id: task-bootstrap-fallback -->
- [x] Run validation suite to confirm compliance <!-- id: task-validation-run -->

## Acceptance Criteria
- [x] Validation suite passes with 11 audits successful.
- [x] MCP tools exit cleanly if current working directory has no valid agent scripts.
- [x] Upgrade script creates backups of modified files.
- [x] Issue close rolls back merge and restores branch on conflict.
- [x] Bootstrap falls back to local templates offline.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [.agents/scripts/mcp_server.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/mcp_server.py)
  - [.agents/scripts/cli/commands/upgrade.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/upgrade.py)
  - [.agents/scripts/cli/commands/issue.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/issue.py)
  - [.agents/scripts/cli/commands/bootstrap.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/bootstrap.py)
- Active module locks:
  - `mcp_server`, `upgrade`, `issue`, `bootstrap`
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
