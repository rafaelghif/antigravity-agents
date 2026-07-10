---
id: issue-235
title: "chore: synchronize installer templates with V3 specifications"
status: closed
assignee: rafaelghif
created_at: 2026-07-10
---

# Issue Details

## Problem Statement
chore: synchronize installer templates with V3 specifications

## Tasks
- [x] Add state ignore rule to antigravityignore.template <!-- id: task-ignore-state-antigravity -->
- [x] Add state ignore rule to gitignore.template <!-- id: task-ignore-state-gitignore -->
- [x] Sync workflow template names to V3 <!-- id: task-workflow-v3 -->

## Acceptance Criteria
- [x] All ignore templates exclude the .agents/state/ directory <!-- id: criteria-ignore-synced -->
- [x] GitHub workflows are correctly named V3 in all action templates <!-- id: criteria-action-synced -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/templates/antigravityignore.template <!-- id: audit-target-files -->
  - [x] .agents/templates/gitignore.template <!-- id: audit-target-files-2 -->
  - [x] .agents/templates/ci_github_workflow.yml.template <!-- id: audit-target-files-3 -->
  - [x] .agents/templates/github-action.yml <!-- id: audit-target-files-4 -->
- Active module locks:
  - [x] github-action <!-- id: lock-github-action -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
