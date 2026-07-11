---
id: issue-278
title: "docs: implement collaboration protocol, security policy, and milestones"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
docs: implement collaboration protocol, security policy, and milestones

## Tasks
- [x] Create .agents/docs/collaboration.md with human-agent guidelines <!-- id: task-create-collaboration-md -->
- [x] Create .agents/memory/security-policy.md with security guidelines <!-- id: task-create-security-policy-md -->
- [x] Create .agents/memory/milestones.md with roadmap details <!-- id: task-create-milestones-md -->

## Acceptance Criteria
- [x] All three markdown files are created and verified <!-- id: criteria-files-created -->
- [x] Validation guard passes without errors <!-- id: criteria-validation-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/docs/collaboration.md, .agents/memory/security-policy.md, .agents/memory/milestones.md <!-- id: audit-target-files -->
- Active module locks:
  - [x] .agents/docs/collaboration, .agents/memory/security-policy, .agents/memory/milestones <!-- id: lock-modules -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
