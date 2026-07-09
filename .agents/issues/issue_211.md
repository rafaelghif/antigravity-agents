---
id: issue-211
title: "Implement agent soul profile and heartbeat workspace diagnostics"
status: closed
assignee: agent-antigravity
created_at: 2026-07-09
---

# Issue Details

## Problem Statement
We need to introduce an agent identity profile `soul.md` and a health-check diagnostic subcommand `heartbeat` to verify workspace state.

## Tasks
- [x] Create agent identity profile `.agents/memory/soul.md` <!-- id: task-create-soul -->
- [x] Implement `heartbeat` command in `.agents/scripts/cli/commands/heartbeat.py` <!-- id: task-create-heartbeat -->
- [x] Register `heartbeat` command in the CLI router `helper.py` <!-- id: task-register-router -->
- [x] Update `AGENTS.md` and `README.md` to reference `soul.md` and `heartbeat` <!-- id: task-update-docs -->
- [x] Run validation suite to confirm compliance <!-- id: task-validation-run -->

## Acceptance Criteria
- [x] Profile file `.agents/memory/soul.md` exists and defines the agent's core values.
- [x] Command `./helper.sh heartbeat` returns lock, budget, and hook diagnostics successfully.
- [x] Validation suite passes.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [.agents/memory/soul.md](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/memory/soul.md)
  - [.agents/scripts/cli/commands/heartbeat.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/heartbeat.py)
  - [.agents/scripts/cli/helper.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/helper.py)
  - [AGENTS.md](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/AGENTS.md)
  - [README.md](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/README.md)
- Active module locks:
  - None
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
