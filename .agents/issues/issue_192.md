---
id: issue-192
title: "Fix project version and changelog mapping during bootstrap and release"
status: open
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
Fix project version and changelog mapping during bootstrap and release

## Tasks
- [x] Implement detect_project_version in bootstrap.py and preserve existing version in AGENTS.md <!-- id: task-1 -->
- [x] Restrict changelog.py wrapper updates to agent core repo and implement native version file bumping <!-- id: task-2 -->
- [x] Run validation suite and verify tests pass <!-- id: task-3 -->

## Acceptance Criteria
- [x] During bootstrap, if AGENTS.md exists or project has version config, the project version is preserved/detected instead of being overwritten by AAC_VERSION.
- [x] Running changelog command does not alter bootstrap.py/sh/ps1 unless in the agent core repository itself.
- [x] Running changelog command successfully bumps project version in AGENTS.md and native files like package.json if present.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [ ] `.agents/scripts/cli/commands/bootstrap.py` <!-- id: audit-target-files -->
  - [ ] `.agents/scripts/cli/commands/changelog.py`
- Active module locks:
  - [ ] `bootstrap` <!-- id: audit-module-locks -->
  - [ ] `changelog`
- Non-negotiable rules checked:
  - [ ] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [ ] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [ ] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
