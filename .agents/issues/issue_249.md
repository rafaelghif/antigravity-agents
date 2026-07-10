---
id: issue-249
title: "feat: refine rule guidelines for skill loading, token efficiency, and working protocol flow"
status: closed
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
Ensure the agent behaves consistently by adding strict rules for skill loading, token/context efficiency, and a clear working protocol flow in `AGENTS.md`.

## Tasks
- [x] Add skill loading and token efficiency guidelines under non-negotiables in `AGENTS.md`. <!-- id: task-agents-rules -->
- [x] Refine Working Protocol Step 9 in `AGENTS.md` for explicit skill file loading. <!-- id: task-protocol-refine -->

## Acceptance Criteria
- [x] Agent is constrained to load skills on-demand and cache search results, improving token efficiency. <!-- id: criteria-rule-constraints -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] `AGENTS.md` <!-- id: audit-target-files -->
- Active module locks:
  - [x] None <!-- id: lock-none -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
