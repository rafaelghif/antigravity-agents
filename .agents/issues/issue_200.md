---
id: issue-200
title: "Document technical alignment and decision capture flow"
status: closed
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
The exact flow of file reads (AGENTS.md -> rules.md -> board.md -> active_context.md -> issues -> schemas -> ADRs) and where technical decisions, feature designs, database models, and self-learning are saved and read must be formally documented to ensure strict alignment. We also need to emphasize the O(1) matching constraint for skills to prevent context bloat.

## Tasks
- [x] Document the Technical Alignment & Decision Capture flow in `AGENTS.md`. <!-- id: subtask-agents-flow -->
- [x] Update `.agents/templates/rules.md.template` and `.agents/rules.md` to enforce the storage routes. <!-- id: subtask-rules-flow -->
- [x] Run validation suite and ensure unit tests pass. <!-- id: subtask-validation -->

## Acceptance Criteria
- [x] `AGENTS.md` lists the exact read/write pathways for `/grill-me`, specifications, database models, and ADRs.
- [x] The rules specify that skills are loaded on demand (O(1) matching constraint) via `view_file` to optimize prompt tokens.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [AGENTS.md](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/AGENTS.md)
  - [.agents/templates/rules.md.template](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/templates/rules.md.template)
  - [.agents/rules.md](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/rules.md)
- Active module locks:
  - `bootstrap` (locked on branch `feat/issue-200`) <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
