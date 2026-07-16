---
id: issue-354
title: "remove global skills caching and enforce workspace isolation"
status: closed
assignee: rafaelghif
created_at: 2026-07-16
---

# Issue Details

## Problem Statement
remove global skills caching and enforce workspace isolation

## Pre-Implementation Impact Analysis
- **Option A (Recommended)**: Completely remove the global caching logic (`cache_skill`) and simplify the installer fallback to only look inside static read-only builtin directories, eliminating global user home writes.
- **Option B**: Keep the global cache but ignore write errors. This still pollutes other projects' skill configurations.

## Tasks
- [x] Task 1: Refactor `.agents/scripts/cli/commands/skill.py` to remove `cache_skill` and global caching references. <!-- id: task-refactor-skill-py -->
- [x] Task 2: Refactor unit tests in `.agents/tests/test_skill.py` to remove global caching test assertions and mocks. <!-- id: task-refactor-test-skill -->
- [x] Task 3: Highlight the removal of global caching in `README.md`. <!-- id: task-update-readme -->
- [x] Task 4: Run validation to verify the changes pass. <!-- id: task-validate -->

## Acceptance Criteria
- [x] Global caching (`cache_skill`) is completely removed from CLI command `skill.py`. <!-- id: ac-no-global-cache -->
- [x] Tests and validation pass without warning or errors. <!-- id: ac-tests-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] `.agents/scripts/cli/commands/skill.py` <!-- id: target-skill -->
  - [x] `.agents/tests/test_skill.py` <!-- id: target-test-skill -->
  - [x] `README.md` <!-- id: target-readme -->
- Active module locks:
  - [ ] None <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
