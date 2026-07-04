---
id: issue-201
title: "Enforce early workspace read of context and schema files"
status: open
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
AI agents often formulate initial plans or assumptions before actually reading the existing workspace specifications (database schema, active issue tasks, and context boundaries). To prevent early-stage design hallucinations, we must mandate that the agent reads `active_context.md`, `schema.md`, and `issue_[id].md` at the start of any conversation session before suggesting designs.

## Tasks
- [x] Mandate early workspace reads of active context and schema files in `AGENTS.md`. <!-- id: subtask-agents-rules -->
- [x] Add the same mandate to `.agents/templates/rules.md.template` and `.agents/rules.md`. <!-- id: subtask-rules-rules -->
- [x] Run validation suite and ensure unit tests pass. <!-- id: subtask-validation -->

## Acceptance Criteria
- [x] The non-negotiable rules require the agent to load and read `active_context.md`, `schema.md`, and the active issue specification at the beginning of the conversation before proposing changes.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [AGENTS.md](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/AGENTS.md)
  - [.agents/templates/rules.md.template](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/templates/rules.md.template)
  - [.agents/rules.md](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/rules.md)
- Active module locks:
  - `bootstrap` (locked on branch `feat/issue-201`) <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
