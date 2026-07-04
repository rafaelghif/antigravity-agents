---
id: issue-197
title: "Add complete transient exclusions to gitignore.template"
status: closed
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
The template `.agents/templates/gitignore.template` does not exclude transient agent runtime states (such as active context, token budget, sync cache, upgrade state, and archived files). When installed in target projects, these files show up as untracked files and can bleed into project git commits.

## Tasks
- [x] Update `.agents/templates/gitignore.template` to exclude all transient files. <!-- id: subtask-gitignore-template -->
- [x] Run validation suite and ensure unit tests pass. <!-- id: subtask-validation -->

## Acceptance Criteria
- [x] `gitignore.template` contains ignores for `.agents/token_budget.json`, `.agents/sync_cache.json`, `.agents/cooldowns.json`, `.agents/upgrade_state.json`, `.agents/active_context.md`, `.agents/archive/`, `.agents/logs/`, `.agents/locks.json`, and `.agents/git_profiles.json`.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [.agents/templates/gitignore.template](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/templates/gitignore.template)
- Active module locks:
  - `bootstrap` (locked on branch `feat/issue-197`) <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
