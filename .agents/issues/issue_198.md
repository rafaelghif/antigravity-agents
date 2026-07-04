---
id: issue-198
title: "Enforce workspace-level plans and artifacts rule"
status: open
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
The AI agent sometimes writes plans, designs, and alignment artifacts to the global `<appDataDir>/brain/<conversation-id>` folder because the standard system instructions for `<artifacts>` suggest doing so. This bypasses workspace-level Git tracking. We must explicitly mandate that all plans and artifacts reside strictly within the project's `.agents/` folder.

## Tasks
- [x] Add the workspace-level artifacts constraint rule to `.agents/templates/rules.md.template`. <!-- id: subtask-rules-template -->
- [x] Add the workspace-level artifacts constraint rule to `.agents/rules.md`. <!-- id: subtask-rules-md -->
- [x] Run validation suite and ensure unit tests pass. <!-- id: subtask-validation -->

## Acceptance Criteria
- [x] Both `rules.md.template` and `rules.md` contain the strict mandate to write plans, designs, specifications, and impact analyses under the workspace's `.agents/` directory (e.g. `.agents/plans/` and `.agents/issues/`), overriding global system paths.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [.agents/templates/rules.md.template](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/templates/rules.md.template)
  - [.agents/rules.md](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/rules.md)
- Active module locks:
  - `bootstrap` (locked on branch `feat/issue-198`) <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
