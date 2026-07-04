---
id: issue-202
title: "Add prompt caching optimization rules"
status: open
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
The agent sometimes re-reads files or re-runs searches that were already completed in previous turns of the same conversation. This causes prompt cache misses and unnecessary token consumption. We must explicitly mandate prompt caching optimization rules.

## Tasks
- [x] Add the prompt caching optimization rule to `.agents/templates/rules.md.template`. <!-- id: subtask-rules-template -->
- [x] Add the prompt caching optimization rule to `.agents/rules.md`. <!-- id: subtask-rules-md -->
- [x] Run validation suite and ensure unit tests pass. <!-- id: subtask-validation -->

## Acceptance Criteria
- [x] Both `rules.md.template` and `rules.md` contain guidelines prohibiting redundant tool calls (like reading the same file twice) and mandating reuse of retrieved information to preserve prompt cache state.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [.agents/templates/rules.md.template](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/templates/rules.md.template)
  - [.agents/rules.md](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/rules.md)
- Active module locks:
  - `bootstrap` (locked on branch `feat/issue-202`) <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
