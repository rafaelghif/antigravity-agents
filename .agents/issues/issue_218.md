---
id: issue-218
title: "Implement CLI skill create scaffolding command"
status: closed
assignee: agent-antigravity
created_at: 2026-07-09
---

# Issue Details

## Problem Statement
Implement CLI skill create scaffolding command

## Tasks
- [x] Add handle_create subcommand parser in skill.py CLI script <!-- id: task-cli-create-subcmd -->
- [x] Implement skill scaffolding generator writing template SKILL.md <!-- id: task-scaffold-generator -->
- [x] Add unit test suite to test_skill.py for validation of create command <!-- id: task-unit-tests -->
- [x] Run validation suite to confirm compliance <!-- id: task-validation-run -->

## Acceptance Criteria
- [x] Running './helper.sh skill create <name> <desc>' scaffolds the directory and template.
- [x] Scaffolder validates skill name input structure (lowercase alphanumeric + hyphens).
- [x] Automatic sync runs to register the skill in AGENTS.md.
- [x] Validation and testing suite passes cleanly.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [.agents/scripts/cli/commands/skill.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/skill.py)
  - [.agents/tests/test_skill.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/tests/test_skill.py) (if it exists, let's check)
- Active module locks:
  - `skill`
  - `validate`
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
