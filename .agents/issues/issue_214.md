---
id: issue-214
title: "Implement installer and bootstrap version checking in validate.py"
status: closed
assignee: agent-antigravity
created_at: 2026-07-09
---

# Issue Details

## Problem Statement
We need to trigger version validation checks inside `validate.py` to audit and prevent platform version drift on installed project repositories.

## Tasks
- [x] Add version checks for `bootstrap.sh` and `bootstrap.ps1` to `validate.py` <!-- id: task-validate-version -->
- [x] Run validation suite to confirm compliance <!-- id: task-validation-run -->

## Acceptance Criteria
- [x] Version validation verifies `bootstrap.sh` and `bootstrap.ps1` version strings match `AGENTS.md`.
- [x] Validation suite passes.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [.agents/scripts/validate.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/validate.py)
- Active module locks:
  - `validate`
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
