---
id: issue-314
title: "feat(blueprints): document blueprints in context map, add MVC and Atomic Design blueprints, and enforce reading rule"
status: closed
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
The `.agents/blueprints/` folder is not currently documented in `context_map.md`, meaning future agent sessions do not know the reference guidelines exist. Furthermore, there are no guidelines for the `mvc` layout choice of the bootstrapper, nor for frontend component hierarchies (such as Atomic Design). Finally, there is no rule in `rules.md` instructing the agent to read these blueprints when designing project modules.

## Tasks
- [x] Move issue-314 to Doing in task board <!-- id: task-move-board -->
- [x] Create .agents/blueprints/mvc-architecture.md <!-- id: task-create-mvc-blueprint -->
- [x] Create .agents/blueprints/atomic-design.md <!-- id: task-create-atomic-blueprint -->
- [x] Add .agents/blueprints/ to context_map.md mappings table <!-- id: task-update-context-map -->
- [x] Add the blueprint loading instruction/rule to rules.md and rules.md.template <!-- id: task-update-rules -->
- [x] Run validation tests and verify workspace compliance <!-- id: task-run-validation -->

## Acceptance Criteria
- [x] `mvc-architecture.md` and `atomic-design.md` blueprints exist under `.agents/blueprints/`. <!-- id: ac-blueprints-created -->
- [x] `context_map.md` correctly maps `.agents/blueprints/` directory. <!-- id: ac-context-mapped -->
- [x] `rules.md` and `rules.md.template` contain the rule directing agents to load blueprints on architectural changes. <!-- id: ac-rules-updated -->
- [x] All validations and tests pass. <!-- id: ac-tests-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/tasks/board.md <!-- id: audit-target-board -->
  - [x] .agents/docs/context_map.md <!-- id: audit-target-context-map -->
  - [x] .agents/rules.md <!-- id: audit-target-rules -->
  - [x] .agents/templates/rules.md.template <!-- id: audit-target-template -->
  - [x] .agents/issues/issue_314.md <!-- id: audit-target-issue -->
- Active module locks:
  - [ ] None <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
