---
id: issue-252
title: "feat: implement pid-based locking, secrets whitelisting, and update monorepo and git profiles documentation"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
Implement robust PID-based locking and secrets whitelisting, and document projects.json and git_profiles.json properties in README.md and context_map.md.

## Tasks
- [x] Implement PID-based locking verification and stale lock deletion in `helper.py`. <!-- id: task-pid-locking -->
- [x] Implement secrets scanner exceptions (ignore test folders, markdown files, and nosec comments) in `validate.py`. <!-- id: task-secrets-whitelisting -->
- [x] Document git_profiles.json, projects.json, and config.json settings in `README.md`. <!-- id: task-readme-doc -->
- [x] Document git_profiles.json, projects.json, and config.json in `.agents/docs/context_map.md`. <!-- id: task-context-map-doc -->

## Acceptance Criteria
- [x] Sandbox locks are automatically pruned if owner process is dead. <!-- id: criteria-pid-locking -->
- [x] Secrets scanning does not false positive on test variables or whitelisted comments. <!-- id: criteria-secrets-whitelisting -->
- [x] Documentation fully covers Monorepos configuration and Git profiles. <!-- id: criteria-doc-coverage -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] `.agents/scripts/cli/helper.py` <!-- id: audit-target-files -->
  - [x] `.agents/scripts/validate.py`
  - [x] `README.md`
  - [x] `.agents/docs/context_map.md`
- Active module locks:
  - [x] .agents/scripts/cli/helper <!-- id: lock-helper -->
  - [x] .agents/scripts/validate <!-- id: lock-validate -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
