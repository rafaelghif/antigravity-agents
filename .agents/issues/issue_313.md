---
id: issue-313
title: "refactor(core): relocate blueprints from memory to agents root and update install and bootstrap commands"
status: closed
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
The architectural blueprints (`clean-architecture.md`, `domain-driven-design.md`, `monorepo.md`) are currently stored under `.agents/memory/blueprints/`. However, `.agents/memory/` represents target project-specific mutable memory. Blueprints are static, framework-level configuration/scaffolding files. Relocating them to `.agents/blueprints/` aligns with the relocation pattern used for `soul.md` and rules. It simplifies installation (avoiding custom `memory/blueprints` copy hacks/exclusions in `install.py`) and keeps `memory/` clean.

## Tasks
- [x] Move issue-313 to Doing in task board <!-- id: task-move-board -->
- [x] Lock bootstrap and install modules <!-- id: task-lock-modules -->
- [x] Move .agents/memory/blueprints to .agents/blueprints in git <!-- id: task-move-directory -->
- [x] Update install.py to remove blueprints-specific copy logic and memory exception <!-- id: task-update-install -->
- [x] Update bootstrap.py to reference .agents/blueprints/ <!-- id: task-update-bootstrap -->
- [x] Run validation tests and verify workspace compliance <!-- id: task-run-validation -->

## Acceptance Criteria
- [x] Blueprints directory is relocated to `.agents/blueprints/`. <!-- id: ac-blueprints-moved -->
- [x] `install.py` handles copying `.agents/blueprints/` naturally via recursive copy. <!-- id: ac-install-clean -->
- [x] `bootstrap.py` initializes `.agents/blueprints/` and all files copy successfully on fresh bootstrap. <!-- id: ac-bootstrap-clean -->
- [x] All unit tests and validation checks pass cleanly. <!-- id: ac-tests-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/tasks/board.md <!-- id: audit-target-board -->
  - [x] .agents/scripts/cli/commands/install.py <!-- id: audit-target-install -->
  - [x] .agents/scripts/cli/commands/bootstrap.py <!-- id: audit-target-bootstrap -->
  - [x] .agents/issues/issue_313.md <!-- id: audit-target-issue -->
- Active module locks:
  - [x] .agents/scripts/cli/commands/bootstrap <!-- id: lock-bootstrap -->
  - [x] .agents/scripts/cli/commands/install <!-- id: lock-install -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
