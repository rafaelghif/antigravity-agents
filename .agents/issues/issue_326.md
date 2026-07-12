---
id: issue-326
title: "feat: append instead of overwrite existing gitignore during installation and bootstrap"
status: open
assignee: agent-antigravity
created_at: 2026-07-12
---

# Issue Details

## Problem Statement
When installing or bootstrapping the Antigravity Agent in an existing project that already has a `.gitignore`, the agent either ignores the `.gitignore` setup completely (leaving agent files untracked) or risks overwriting it if forced.
We need to:
1. Define clear markers (`# <<< ANTIGRAVITY AGENT START >>>` and `# <<< ANTIGRAVITY AGENT END >>>`) around the agent-specific ignore rules in the `.agents/templates/gitignore.template` file.
2. Implement an `ensure_gitignore_entries(src_root, target_dir)` utility function in `.agents/scripts/cli/commands/bootstrap.py` that reads the template, extracts the block, and cleanly writes/updates/appends it to the target `.gitignore`.
3. Call `ensure_gitignore_entries(src_root, ".")` in `bootstrap.py` instead of the old conditional creation logic.
4. Write comprehensive unit tests in `.agents/tests/test_bootstrap.py` to cover creation, appending, and in-place upgrading.

## Tasks
- [x] Wrap agent ignores in `.agents/templates/gitignore.template` inside block markers. <!-- id: task-gitignore-template -->
- [x] Implement `ensure_gitignore_entries` function in `bootstrap.py`. <!-- id: task-ensure-gitignore-fn -->
- [x] Replace old `.gitignore` conditional write in `bootstrap.py` with `ensure_gitignore_entries(src_root, ".")`. <!-- id: task-call-ensure-gitignore -->
- [x] Add comprehensive unit tests for `ensure_gitignore_entries` in `test_bootstrap.py`. <!-- id: task-add-unit-tests -->
- [x] Run validation checks to ensure tests and compliance pass successfully. <!-- id: task-run-validation -->

## Acceptance Criteria
- [x] If `.gitignore` does not exist in target directory, it is created with full template rules. <!-- id: crit-create-gitignore -->
- [x] If `.gitignore` exists without markers, the agent block is appended to the end of the file. <!-- id: crit-append-gitignore -->
- [x] If `.gitignore` exists with markers, the agent block is replaced/updated in-place. <!-- id: crit-update-gitignore -->
- [x] Validation guard checks pass successfully. <!-- id: crit-validation-passes -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/templates/gitignore.template <!-- id: audit-target-files -->
  - [x] .agents/scripts/cli/commands/bootstrap.py
  - [x] .agents/tests/test_bootstrap.py
- Active module locks:
  - [x] .agents/scripts/cli/commands/bootstrap <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
