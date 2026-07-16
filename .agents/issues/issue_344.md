---
id: 344
title: "feat: relax validation checks for human programmers to allow warning-only bypasses"
status: open
assignee: agent-antigravity
created_at: 2026-07-16
---

# Issue Details

## Problem Statement
The current validation checks are too strict for human developers. When running validations or closing issues, human developers get blocked by unresolved subtasks, static linting failures, or unit test failures. We need to:
1. Make "Static Code Linting" and "Local Unit Tests" warn-only/bypassed audits when run by a human programmer (`ANTIGRAVITY_AGENT != "1"`).
2. Allow human programmers to bypass the unresolved required subtasks check (warn-only) when running validations/closing issues.

## Tasks
- [x] Relax unresolved required subtasks check for human mode in `.agents/scripts/validate.py` <!-- id: task-validate-subtasks -->
- [x] Add static linting and unit tests to `bureaucratic_audits` for human bypass mode in `.agents/scripts/validate.py` <!-- id: task-validate-audits -->
- [x] Update `.agents/templates/rules.md.template` to document this human relaxation rule <!-- id: task-rules-template -->
- [x] Update `.agents/rules.md` to document this human relaxation rule <!-- id: task-rules-core -->
- [x] Verify validation passes cleanly under human and agent modes <!-- id: task-verify -->

## Acceptance Criteria
- [x] A human programmer is not blocked by failing unit tests, static linting, or unresolved subtasks <!-- id: ac-relaxed -->
- [x] Validation command `./helper.sh validate` passes cleanly <!-- id: ac-validation -->

## Pre-Implementation Impact Analysis
- **Option A**: Remove checks entirely for humans.
  - *Pros*: Very loose.
  - *Cons*: Humans might commit severe security issues or critical files mistakes without realizing it.
- **Option B (Recommended)**: Demote quality/bureaucratic checks (linting, tests, branch naming, subtasks checklist) to warn-only bypassed checks in human mode, while keeping security/critical checks (secrets, critical files check) active, and allowing easy bypass.
  - *Pros*: High usability without compromising repo safety. Fully aligns with the user's request.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] `.agents/scripts/validate.py` <!-- id: target-validate -->
  - [x] `.agents/templates/rules.md.template` <!-- id: target-rules-template -->
  - [x] `.agents/rules.md` <!-- id: target-rules-core -->
- Active module locks:
  - [x] `.agents/scripts/validate.py` locked <!-- id: audit-validate-lock -->
  - [x] `.agents/rules.md` locked <!-- id: audit-rules-lock -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
