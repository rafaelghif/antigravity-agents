---
id: 342
title: "fix: enforce strict agent script isolation rule in AGENTS.md template"
status: closed
assignee: rafaelghif
created_at: 2026-07-16
github_url: "https://github.com/rafaelghif/antigravity-agents/issues/48"
github_number: 48
---

# Issue Details

## Problem Statement
In target projects, the agent should have a strict, non-negotiable rule in its prompt context (`AGENTS.md`) preventing it from modifying or analyzing any agent-internal scripts (`.agents/scripts/`, etc.) unless it is developing the agent core repository itself. This will provide a strong prompt-level guardrail to prevent self-repair leaks.

## Tasks
- [x] Add the non-negotiable script isolation rule to `AGENTS.md.template` <!-- id: task-update-agents-template -->
- [x] Add the non-negotiable script isolation rule to the core repo's `AGENTS.md` <!-- id: task-update-agents-core -->
- [x] Verify validation passes cleanly <!-- id: ac-validation-pass -->

## Acceptance Criteria
- [x] Validation guard runs and passes cleanly <!-- id: ac-validation-clean -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] `.agents/templates/AGENTS.md.template` <!-- id: target-agents-template -->
  - [x] `AGENTS.md` <!-- id: target-agents-core -->
- Active module locks:
  - [x] None <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
