---
id: issue-224
title: "Implement V3 Phase 3: Proactive Budget Guard & Auto-Repairing"
status: closed
assignee: agent-antigravity
created_at: 2026-07-09
---

# Issue Details

## Problem Statement
Implement V3 Phase 3: Proactive Budget Guard & Auto-Repairing

## Tasks
- [x] Implement active budget gate check in helper.py to block token-consuming commands on budget overrun <!-- id: task-budget-gate -->
- [x] Implement perform_repairs() in doctor.py to auto-heal configs, stale locks, and git hooks <!-- id: task-doctor-repair -->
- [x] Add --repair option to doctor command to trigger perform_repairs() first <!-- id: task-doctor-flag -->
- [x] Implement unit tests for the budget gate and doctor repair hooks <!-- id: task-unit-tests -->
- [x] Run validation suite to confirm compliance <!-- id: task-validate-run -->

## Acceptance Criteria
- [x] helper.py successfully blocks executing subcommands when budget limits are exceeded, showing a clear warning (except token, doctor, and upgrade).
- [x] doctor.py implements perform_repairs() which automatically restores missing/corrupt configs, prunes stale locks, and repairs git hooks.
- [x] Running `./helper.sh doctor --repair` executes all repairs first, followed by diagnostics checks.
- [x] All tests pass successfully.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [.agents/scripts/cli/helper.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/helper.py) <!-- id: audit-target-helper -->
  - [.agents/scripts/cli/commands/doctor.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/doctor.py) <!-- id: audit-target-doctor -->
- Active module locks:
  - `helper` <!-- id: audit-module-helper -->
  - `doctor` <!-- id: audit-module-doctor -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
