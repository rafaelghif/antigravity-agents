---
id: issue-348
title: "Implement AI skill loading enforcer in validation checks"
status: Doing
assignee: rafaelghif
created_at: 2026-07-16
---

# Issue Details

## Problem Statement
The agent core needs a programmatic enforcer to guarantee that the AI agent strictly loads and reads the relevant skill playbook file (via `view_file` on `.agents/skills/<name>/SKILL.md`) when modifying files or running commands associated with that skill, preventing speculative execution or ignoring project-specific playbooks.

## Tasks
- [x] Implement skill playbook loading enforcer in `validate.py` <!-- id: task-enforce-skill-loading -->
- [x] Test new validation logic by loading playbooks on-demand <!-- id: task-test-validation -->
- [x] Validate and sync all changes <!-- id: task-validate-sync -->

## Acceptance Criteria
- [x] AI agent is blocked from committing or validating if a required skill playbook was not viewed <!-- id: ac-block-agent -->
- [x] Validation successfully passes when all required playbooks are viewed <!-- id: ac-pass-validation -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] `.agents/scripts/validate.py` <!-- id: target-validate -->
- Active module locks:
  - [x] validate.py locked <!-- id: audit-lock-validate -->
