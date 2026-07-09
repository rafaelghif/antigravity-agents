---
id: issue-228
title: "Implement V4 Phase 2: Git-Native Concurrency Locking"
status: open
assignee: corporate-work
created_at: 2026-07-09
---

# Issue Details

## Problem Statement
Implement V4 Phase 2: Git-Native Concurrency Locking

## Tasks
- [x] Implement Git-Native lock storage and query parser in `commands/lock.py` <!-- id: task-lock-impl -->
- [x] Update `validate.py`, `commands/dashboard.py`, `commands/doctor.py`, and `run_benchmarks.py` to use git-native lock loader <!-- id: task-refs-update -->
- [x] Update unit tests in `test_lock.py`, `test_doctor.py`, `test_dashboard.py`, and `test_validate.py` <!-- id: task-tests-update -->
- [x] Run full validation suite and verify all tests pass successfully <!-- id: task-validation-run -->

## Acceptance Criteria
- [x] Module locks are declared strictly within the branch's active issue markdown file under Active module locks.
- [x] Locks are queried dynamically across branches using Git operations, with zero dependency on locks.json.
- [x] All 192 unit tests pass successfully.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/scripts/cli/commands/lock.py <!-- id: audit-target-lock -->
  - [x] .agents/scripts/cli/commands/issue.py <!-- id: audit-target-issue -->
  - [x] .agents/scripts/cli/commands/dashboard.py <!-- id: audit-target-dashboard -->
  - [x] .agents/scripts/cli/commands/doctor.py <!-- id: audit-target-doctor -->
  - [x] .agents/scripts/validate.py <!-- id: audit-target-validate -->
  - [x] .agents/scripts/run_benchmarks.py <!-- id: audit-target-benchmarks -->
- Active module locks:
  - [ ] .agents/scripts/cli/commands/lock <!-- id: lock-lock -->
  - [ ] .agents/scripts/cli/commands/issue <!-- id: lock-issue -->
  - [ ] .agents/scripts/cli/commands/dashboard <!-- id: lock-dashboard -->
  - [ ] .agents/scripts/cli/commands/doctor <!-- id: lock-doctor -->
  - [ ] .agents/scripts/validate <!-- id: lock-validate -->
  - [ ] .agents/scripts/run_benchmarks <!-- id: lock-run_benchmarks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
