---
id: issue-274
title: "feat: relocate soul.md to .agents root"
status: closed
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
feat: relocate soul.md to .agents root

## Tasks
- [x] Relocate soul.md from .agents/memory/ to .agents/ root <!-- id: task-relocate-soul -->
- [x] Create ADR 0004 for relocating soul.md <!-- id: task-create-adr -->
- [x] Update heartbeat.py to point to .agents/soul.md <!-- id: task-update-heartbeat -->
- [x] Update context_map.md path for soul.md <!-- id: task-update-context-map -->
- [x] Update bootstrap.py core copy list to include .agents/soul.md <!-- id: task-update-bootstrap -->
- [x] Link ADR 0004 in architecture.md registry <!-- id: task-update-architecture -->

## Acceptance Criteria
- [x] Validation guard passes without soul.md heartbeat warning <!-- id: criteria-validation-pass -->
- [x] soul.md is placed directly in .agents/ folder <!-- id: criteria-soul-path -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/memory/soul.md, .agents/scripts/cli/commands/heartbeat.py, .agents/docs/context_map.md, .agents/scripts/cli/commands/bootstrap.py, .agents/memory/architecture.md <!-- id: audit-target-files -->
- Active module locks:
  - [ ] .agents/scripts/cli/commands/bootstrap <!-- id: lock-bootstrap -->
  - [ ] .agents/scripts/cli/commands/heartbeat <!-- id: lock-heartbeat -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
