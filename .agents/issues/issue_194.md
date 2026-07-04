---
id: issue-194
title: "Exclude active context logs and budgets from installer"
status: closed
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
The installer copies active development files (such as `active_context.md`, `token_budget.json`, `sync_cache.json`, `cooldowns.json`, `upgrade_state.json`, and `schema.md`) and directories (such as `archive/` and `logs/`) from the core agent repository to target project directories. This leaks active context and token ledger logs to target projects, causing memory mixing.

## Tasks
- [x] Exclude transient and memory files/directories in `install.sh`. <!-- id: subtask-install-sh -->
- [x] Exclude transient and memory files/directories in `install.ps1`. <!-- id: subtask-install-ps1 -->
- [x] Run validation suite and ensure unit tests pass. <!-- id: subtask-validation -->

## Acceptance Criteria
- [x] Installer scripts `install.sh` and `install.ps1` exclude `active_context.md`, `token_budget.json`, `archive/`, `logs/`, `upgrade_state.json`, `sync_cache.json`, `cooldowns.json`, and `schema.md` from copy logic.
- [x] All unit and integration tests run and pass.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [install.sh](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/install.sh)
  - [install.ps1](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/install.ps1)
- Active module locks:
  - [x] None <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
