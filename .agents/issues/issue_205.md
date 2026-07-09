---
id: issue-205
title: "Enhance plug-and-play adaptability, zero leakage boundaries, and local workspace memory support"
status: closed
assignee: agent-antigravity
created_at: 2026-07-09
---

# Issue Details

## Problem Statement
We need to ensure absolute workspace isolation, plug-and-play adaptability, and zero leakage of developer states:
1. Local bootstrapping should never leak transient state files like `token_budget.json`, `active_context.md`, `sync_cache.json`, etc. from the parent framework workspace.
2. Custom target workspace memory structures (such as `memory.md` or `brain.md` in the project root or `.agents/`) must be recognized, read, and maintained locally on the workspace level, keeping the agent fully based on local project context rather than global configurations.

## Tasks
- [x] Harden copy-exclusion files list in `is_ignored()` in [bootstrap.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/bootstrap.py) <!-- id: task-bootstrap-exclusions -->
- [x] Update rules in [AGENTS.md](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/AGENTS.md) to enforce local workspace memory read/write boundaries <!-- id: task-agents-rules -->
- [x] Update active [.agents/rules.md](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/rules.md) with workspace memory guidelines <!-- id: task-active-rules -->
- [x] Update [.agents/templates/rules.md.template](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/templates/rules.md.template) with workspace memory guidelines <!-- id: task-template-rules -->
- [x] Run validation suite to confirm compliance <!-- id: task-validation-run -->

## Acceptance Criteria
- [x] Local bootstrapping ignores all active transient logs and config files.
- [x] `AGENTS.md` and rules dictate strict loading and writing of workspace-level files like `memory.md` and `brain.md`.
- [x] No global configurations or directory caches are leaked between distinct workspaces.
- [x] All unit tests pass successfully.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [bootstrap.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/bootstrap.py)
  - [AGENTS.md](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/AGENTS.md)
  - [.agents/rules.md](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/rules.md)
  - [.agents/templates/rules.md.template](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/templates/rules.md.template)
- Active module locks:
  - `bootstrap`
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
