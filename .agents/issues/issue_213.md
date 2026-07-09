---
id: issue-213
title: "Enforce dependency mapping and installer validation rules in core files"
status: closed
assignee: agent-antigravity
created_at: 2026-07-09
---

# Issue Details

## Problem Statement
We need to introduce strict directives in `soul.md`, `rules.md`, templates, and `AGENTS.md` forcing the agent to always verify bootstrap and installer scripts across Linux and Windows for parity, and maintain dependency mapping records.

## Tasks
- [x] Update `soul.md` to append dependency verification values <!-- id: task-update-soul -->
- [x] Update `AGENTS.md` to append installer audit rules <!-- id: task-update-agents -->
- [x] Update `rules.md` and `rules.md.template` with installer audit rules <!-- id: task-update-rules -->
- [x] Run validation suite to confirm compliance <!-- id: task-validation-run -->

## Acceptance Criteria
- [x] Identity profile `soul.md` mandates installer and bootstrap alignment checks.
- [x] Master rules lists specify dependency mapping checks.
- [x] Validation suite passes.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [AGENTS.md](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/AGENTS.md)
  - [.agents/rules.md](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/rules.md)
  - [.agents/templates/rules.md.template](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/templates/rules.md.template)
  - [.agents/memory/soul.md](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/memory/soul.md)
- Active module locks:
  - None
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
