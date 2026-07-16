---
id: issue-351
title: "Consolidate and expand agent skills playbooks"
status: open
assignee: rafaelghif
created_at: 2026-07-16
---

# Issue Details

## Problem Statement
Consolidate and expand agent skills playbooks

## Tasks
- [x] Task 1: Consolidate and de-duplicate rules across `coding-standards/SKILL.md`, `code-review/SKILL.md`, `testing/SKILL.md`, `adr/SKILL.md`, and `security-audit/SKILL.md`. <!-- id: task-consolidate -->
- [x] Task 2: Scaffold and populate the new `refactoring` skill playbook. <!-- id: task-refactoring -->
- [x] Task 3: Scaffold and populate the new `documentation` skill playbook. <!-- id: task-documentation -->
- [x] Task 4: Scaffold and populate the new `compliance` skill playbook. <!-- id: task-compliance -->
- [x] Task 5: Run validation audits to verify sync and pass status. <!-- id: task-validate -->

## Acceptance Criteria
- [x] Duplicated code review, testing, and secret security rules are consolidated. <!-- id: ac-consolidate -->
- [x] New skill directories `refactoring`, `documentation`, and `compliance` exist and contain compliant `SKILL.md` frontmatter and guides. <!-- id: ac-new-skills -->
- [x] `./helper.sh validate` passes successfully with zero warnings/errors. <!-- id: ac-validate -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] `.agents/skills/coding-standards/SKILL.md` <!-- id: target-coding-standards -->
  - [x] `.agents/skills/code-review/SKILL.md` <!-- id: target-code-review -->
  - [x] `.agents/skills/testing/SKILL.md` <!-- id: target-testing -->
  - [x] `.agents/skills/adr/SKILL.md` <!-- id: target-adr -->
  - [x] `.agents/skills/security-audit/SKILL.md` <!-- id: target-security-audit -->
  - [x] `.agents/skills/refactoring/SKILL.md` <!-- id: target-refactoring -->
  - [x] `.agents/skills/documentation/SKILL.md` <!-- id: target-documentation -->
  - [x] `.agents/skills/compliance/SKILL.md` <!-- id: target-compliance -->
- Active module locks:
  - [x] `coding-standards` <!-- id: lock-coding-standards -->
  - [x] `code-review` <!-- id: lock-code-review -->
  - [x] `testing` <!-- id: lock-testing -->
  - [x] `adr` <!-- id: lock-adr -->
  - [x] `security-audit` <!-- id: lock-security-audit -->
  - [x] `refactoring` <!-- id: lock-refactoring -->
  - [x] `documentation` <!-- id: lock-documentation -->
  - [x] `compliance` <!-- id: lock-compliance -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
