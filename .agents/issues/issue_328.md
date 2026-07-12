---
id: issue-328
title: "feat: default bootstrap architecture to none to prevent accidental scaffolding"
status: open
assignee: agent-antigravity
created_at: 2026-07-12
---

# Issue Details

## Problem Statement
We want to ensure that scaffolding is **disabled by default** when running the project bootstrapper (`bootstrap.py`), rather than defaulting to `clean` or `mvc`.
We need to:
1. Change the default architecture `arch` to `"none"` in quick setup mode, interactive prompt default, and positional arguments parsing.
2. Determine the `scaffold` boolean value dynamically based on whether a scaffolding architecture (`clean`, `layered`, `mvc`) is explicitly chosen and not overridden by `--no-scaffold`.
3. Update unit tests in `test_bootstrap.py` to assert that running bootstrap without arguments defaults to no scaffolding (no `src/` directory created).

## Tasks
- [x] Change bootstrap default architectures to `"none"` in `bootstrap.py`. <!-- id: task-none-default -->
- [x] Determine `scaffold` dynamically from `arch` and the `--no-scaffold` flag. <!-- id: task-dynamic-scaffold -->
- [x] Update unit tests in `test_bootstrap.py` to align with the new defaults. <!-- id: task-update-tests -->
- [x] Run validation checks to ensure tests and compliance pass successfully. <!-- id: task-run-validation -->

## Acceptance Criteria
- [x] Default bootstrap mode (quick mode, default interactive input, or no-argument execution) defaults to `"none"` architecture. <!-- id: crit-none-by-default -->
- [x] Scaffolding is skipped unless `clean`, `layered`, or `mvc` is explicitly specified. <!-- id: crit-scaffold-skipped -->
- [x] Validation check passes successfully. <!-- id: crit-validation-passes -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/scripts/cli/commands/bootstrap.py <!-- id: audit-target-files -->
  - [x] .agents/tests/test_bootstrap.py
- Active module locks:
  - [x] .agents/scripts/cli/commands/bootstrap <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
