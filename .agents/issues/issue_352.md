---
id: issue-352
title: "Optimize skill loading rules in agents and rules templates"
status: open
assignee: rafaelghif
created_at: 2026-07-16
---

# Issue Details

## Problem Statement
Optimize skill loading rules in agents and rules templates

## Pre-Implementation Impact Analysis
- **Option A (Recommended)**: Proactively rewrite the skill enforcer rules in both active files and templates to encourage loading skills at the start of relevant tasks/subtasks, rather than restricting it to a reactive validation gate.
- **Option B**: Modify only the active files, causing them to get overwritten during future bootstrapping/upgrades.

## Tasks
- [x] Task 1: Update skill loading rules in active files `AGENTS.md` and `.agents/rules.md`. <!-- id: task-update-active -->
- [x] Task 2: Update skill loading rules in templates `.agents/templates/AGENTS.md.template` and `.agents/templates/rules.md.template`. <!-- id: task-update-templates -->
- [x] Task 3: Run validation to verify the rules and templates pass checks. <!-- id: task-validate -->

## Acceptance Criteria
- [x] Active rules and templates contain the new proactive skill loading guidelines. <!-- id: ac-proactive-rules -->
- [x] `./helper.sh validate` runs and completes successfully. <!-- id: ac-validate -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] `AGENTS.md` <!-- id: target-agents -->
  - [x] `.agents/rules.md` <!-- id: target-rules -->
  - [x] `.agents/templates/AGENTS.md.template` <!-- id: target-agents-template -->
  - [x] `.agents/templates/rules.md.template` <!-- id: target-rules-template -->
- Active module locks:
  - [x] `rules` <!-- id: lock-rules -->
  - [x] `agents` <!-- id: lock-agents -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
