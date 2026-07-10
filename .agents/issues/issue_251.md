---
id: issue-251
title: "docs: update README.md with new CLI command flags and config settings"
status: closed
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
Ensure the agent's main README.md accurately documents all new CLI options, flags, commands, and settings config files.

## Tasks
- [x] Update `README.md` command reference table with `-q`, `-i`, `--clear-all`, `--prune`, `pause`, `resume`, and token default status subcommands. <!-- id: task-readme-table-update -->
- [x] Document the new `.agents/config.json` advanced workspace setting configuration `"workflow_mode": "solo"`. <!-- id: task-advanced-settings-doc -->

## Acceptance Criteria
- [x] `README.md` documents all new features and configurations. <!-- id: criteria-readme-aligned -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] `README.md` <!-- id: audit-target-files -->
- Active module locks:
  - [x] None <!-- id: lock-none -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
