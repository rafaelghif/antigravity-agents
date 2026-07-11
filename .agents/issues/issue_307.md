---
id: issue-307
title: "Enforce agent soul profile in AGENTS.md and enhance soul personality strictness"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
We need to enforce that the AI agent strictly conforms to the persona, values, and guidelines defined in `.agents/soul.md` by explicitly referencing and enforcing it within the prepended core rules file `AGENTS.md`. We also need to enhance `.agents/soul.md` to be even more strictly engineering-focused, professional, and zero-fluff to prevent personality drift across different developer accounts and API profiles.

## Tasks
- [x] Add strict soul.md enforcement rule to AGENTS.md <!-- id: task-update-agents-md -->
- [x] Enhance soul.md guidelines with enterprise-grade engineering tone and behavioral rules <!-- id: task-update-soul-md -->
- [x] Lock modified modules and verify locks <!-- id: task-acquire-locks -->
- [x] Run validation tests and verify workspace compliance <!-- id: task-run-validation -->

## Acceptance Criteria
- [x] `AGENTS.md` contains a non-negotiable rule requiring the agent to strictly load and adhere to `.agents/soul.md` in every response and action. <!-- id: ac-agents-rule-added -->
- [x] `.agents/soul.md` is enhanced with a section enforcing professional tone, "no fluff/pleasantries", and consistent technical identity. <!-- id: ac-soul-enhanced -->
- [x] Local validation guard passes cleanly. <!-- id: ac-validation-passes -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/tasks/board.md <!-- id: audit-target-board -->
  - [x] AGENTS.md <!-- id: audit-target-agents -->
  - [x] .agents/soul.md <!-- id: audit-target-soul -->
  - [x] .agents/issues/issue_307.md <!-- id: audit-target-issue -->
- Active module locks:
  - [x] AGENTS.md <!-- id: lock-AGENTS_md -->
  - [x] .agents/soul.md <!-- id: lock-soul_md -->
- Non-negotiable rules checked:
  - [ ] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [ ] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [ ] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
