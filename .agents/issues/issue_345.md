---
id: issue-345
title: "feat: Implement initial model/entity definitions"
status: open
assignee: agent-antigravity
created_at: 2026-07-16
---

# Design & Task Specification

## Technical Decisions
We will introduce formal Python `dataclasses` representing the core domain concepts of the workspace to replace direct dictionary manipulation:
- `GitProfile` (representing a developer Git signature and authentication keys).
- `ModuleLock` (representing a lock held on a codebase file).
- `TokenBudget` (representing token limits and usage).
- `Issue` (representing a local task or issue specification).

All entities will reside in a new package `core` under `.agents/scripts/core/entities.py`.

## Tasks
- [x] Create domain entities file `.agents/scripts/core/entities.py` and package initialization <!-- id: task-create-entities -->
- [x] Integrate entities into profile and commit logic <!-- id: task-integrate-profile -->
- [x] Integrate entities into lock service logic <!-- id: task-integrate-lock -->
- [x] Integrate entities into token service logic <!-- id: task-integrate-token -->
- [x] Integrate entities into issue service logic <!-- id: task-integrate-issue -->
- [x] Write unit tests under `.agents/tests/test_entities.py` <!-- id: task-write-tests -->
- [x] Run sync and validation checks to verify correctness <!-- id: task-sync-validate -->

## Acceptance Criteria
- [x] Core services load and save models cleanly <!-- id: ac-integration -->
- [x] Entities validation blocks invalid fields correctly <!-- id: ac-validation -->
- [x] Validator suite passes successfully <!-- id: ac-success -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] `.agents/scripts/core/entities.py` <!-- id: target-entities -->
  - [x] `.agents/scripts/cli/commands/profile.py` <!-- id: target-profile -->
  - [x] `.agents/scripts/cli/commands/commit.py` <!-- id: target-commit -->
  - [x] `.agents/scripts/cli/commands/services/lock_service.py` <!-- id: target-lock-service -->
  - [x] `.agents/scripts/cli/commands/services/token_service.py` <!-- id: target-token-service -->
  - [x] `.agents/scripts/cli/commands/services/issue_service.py` <!-- id: target-issue-service -->
  - [x] `.agents/tests/test_entities.py` <!-- id: target-tests -->
- Active module locks:
  - [x] lock_service.py locked <!-- id: audit-lock-service -->
  - [x] token_service.py locked <!-- id: audit-token-service -->
  - [x] issue_service.py locked <!-- id: audit-issue-service -->
  - [x] profile.py locked <!-- id: audit-profile -->
  - [x] commit.py locked <!-- id: audit-commit -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
