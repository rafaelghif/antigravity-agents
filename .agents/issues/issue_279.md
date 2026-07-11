---
id: issue-279
title: "fix: synchronize installation templates for milestones and security policy"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
fix: synchronize installation templates for milestones and security policy

## Tasks
- [x] Create .agents/memory/templates/security-policy.md.template <!-- id: task-create-security-policy-template -->
- [x] Create .agents/memory/templates/milestones.md.template <!-- id: task-create-milestones-template -->
- [x] Document the new template relationships inside .agents/docs/template_map.md <!-- id: task-update-template-map -->

## Acceptance Criteria
- [x] New templates exist and match target documents <!-- id: criteria-templates-exist -->
- [x] Validation guard passes successfully <!-- id: criteria-validation-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/memory/templates/security-policy.md.template, .agents/memory/templates/milestones.md.template, .agents/docs/template_map.md <!-- id: audit-target-files -->
- Active module locks:
  - [x] .agents/memory/templates, .agents/docs/template_map <!-- id: lock-modules -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
