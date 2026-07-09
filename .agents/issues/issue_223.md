---
id: issue-223
title: "Implement V3 Phase 2: Active Skill Contracts & Swarm Handoffs"
status: closed
assignee: agent-antigravity
created_at: 2026-07-09
---

# Issue Details

## Problem Statement
Implement V3 Phase 2: Active Skill Contracts & Swarm Handoffs

## Tasks
- [x] Update sync.py to scan custom skills and generate skills registry <!-- id: task-sync-index -->
- [x] Update validate.py to load and execute custom skill validation hooks from the registry <!-- id: task-validate-hooks -->
- [x] Develop the .agents/messages/ peer messaging command in the CLI <!-- id: task-message-cmd -->
- [x] Implement unit tests for active skill indexing and peer messaging <!-- id: task-unit-tests -->
- [x] Run validation suite to confirm compliance <!-- id: task-validate-run -->

## Acceptance Criteria
- [x] Active skill validation hooks are indexed in .agents/skills/registry.json during sync.
- [x] validate.py automatically executes custom skill validation hooks and displays results.
- [x] CLI command helper.sh message supports sending, listing, and updating peer messages.
- [x] Validation suite passes successfully.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [.agents/scripts/sync.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/sync.py) <!-- id: audit-target-sync -->
  - [.agents/scripts/validate.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/validate.py) <!-- id: audit-target-validate -->
  - [.agents/scripts/cli/commands/message.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/message.py) <!-- id: audit-target-message -->
- Active module locks:
  - `sync` <!-- id: audit-module-locks -->
  - `helper`
  - `validate`
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
