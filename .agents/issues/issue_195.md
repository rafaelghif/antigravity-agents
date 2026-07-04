---
id: issue-195
title: "Fix upgrade.py to exclude AGENTS.md and rules.md from auto-checkout"
status: closed
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
When `helper.sh upgrade` or the auto-upgrader is executed inside a target project, it fetches from the core agent repository and runs `git checkout FETCH_HEAD` on `AGENTS.md` and `.agents/rules.md`. This overwrites the target project's personalized product/rules with the core repository rules, causing project configuration pollution.

## Tasks
- [x] Remove `AGENTS.md` and `.agents/rules.md` from `paths_to_update` in `upgrade.py`. <!-- id: subtask-upgrade-paths -->
- [x] Run validation suite and ensure unit tests pass. <!-- id: subtask-validation -->

## Acceptance Criteria
- [x] `upgrade.py` only upgrades `.agents/scripts/`, `.agents/templates/`, `.agents/skills/`, `helper.sh`, and `helper.ps1`.
- [x] Upgrades do not overwrite local `AGENTS.md` and `.agents/rules.md`.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [.agents/scripts/cli/commands/upgrade.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/upgrade.py)
- Active module locks:
  - `upgrade` (locked on branch `feat/issue-195`) <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
