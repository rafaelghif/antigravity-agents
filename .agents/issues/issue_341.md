---
id: 341
title: "fix: exclude agent changelog/memory from target installations and isolate agent scripts in antigravityignore"
status: Doing
assignee: rafaelghif
created_at: 2026-07-16
---

# Issue Details

## Problem Statement
When installing/bootstrapping the agent in a target project, the agent's own `CHANGELOG.md` and filled memory files (lessons-learned, milestones, security-policy, architecture, glossary, etc.) are copied directly into the target project instead of starting fresh or using clean templates. Additionally, the agent is not isolated from searching and attempting to "repair" its own implementation scripts (`.agents/scripts/`, `.agents/workflows/`, etc.) in target projects.

## Tasks
- [x] Create `lessons-archive.md.template` in `.agents/memory/templates/` <!-- id: task-create-lessons-archive-template -->
- [x] Update `install.py` to remove `CHANGELOG.md`, `README.md`, `Dockerfile`, and the memory files from `copy_if_missing_filenames` <!-- id: task-update-install-copy-list -->
- [x] Update `bootstrap.py` to append agent-internal paths (`.agents/scripts/`, `.agents/workflows/`, `.agents/dashboard/`, `.agents/templates/`) to `.antigravityignore` in target projects to isolate them <!-- id: task-update-bootstrap-ignore -->
- [x] Update `test_install.py` to align with the updated `copy_if_missing_filenames` logic <!-- id: task-update-install-tests -->

## Acceptance Criteria
- [x] Unit tests pass successfully <!-- id: ac-tests-pass -->
- [x] The validation guard passes cleanly <!-- id: ac-validation-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] `.agents/scripts/cli/commands/install.py` <!-- id: target-install-py -->
  - [x] `.agents/scripts/cli/commands/bootstrap.py` <!-- id: target-bootstrap-py -->
  - [x] `.agents/memory/templates/lessons-archive.md.template` <!-- id: target-lessons-archive-template -->
  - [x] `.agents/tests/test_install.py` <!-- id: target-test-install-py -->
- Active module locks:
  - [x] install <!-- id: lock-install -->
  - [x] bootstrap <!-- id: lock-bootstrap -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
