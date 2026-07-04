---
id: issue-199
title: "Synchronize antigravityignore.template exclusions with active ignore rules"
status: closed
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
The template `.agents/templates/antigravityignore.template` does not contain all the ignore patterns defined in the active `.antigravityignore` file. This means target projects will not exclude local transient files (budgets, caches, contexts, logs, etc.) from the agent's file indexing and search operations, leading to potential search leakage and prompt pollution.

## Tasks
- [x] Update `.agents/templates/antigravityignore.template` to exclude all transient files. <!-- id: subtask-antigravityignore-template -->
- [x] Run validation suite and ensure unit tests pass. <!-- id: subtask-validation -->

## Acceptance Criteria
- [x] `antigravityignore.template` contains identical `.agents/` ignore rules to `.antigravityignore` (including `locks/`, `api_keys`, `active_context.md`, `cooldowns.json`, `sync_cache.json`, `logs/`, `archive/`, `upgrade_state.json`, and `token_budget.json`).

## Rule & Schema Compliance Audit
- Target files to edit:
  - [.agents/templates/antigravityignore.template](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/templates/antigravityignore.template)
- Active module locks:
  - `bootstrap` (locked on branch `feat/issue-199`) <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
