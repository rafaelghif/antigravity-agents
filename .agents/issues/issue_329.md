---
id: 329
title: "feat: relax codebase search and file retrieval redundancy constraints to allow deeper analysis"
status: closed
assignee: rafaelghif
created_at: 2026-07-12
---

# Issue Details

## Problem Statement
The current rules in `AGENTS.md` and `.agents/rules.md` strictly prohibit retrieving the same files or running the same codebase searches more than once per task/session. While this saves tokens, it prevents the agent from re-evaluating modified files, verifying state updates, or conducting deeper, iterative analyses on critical files. We need to relax these constraints.

## Pre-Implementation Impact Analysis
- **Option 1: Complete Removal**: Delete all references to search/retrieval limits.
  - *Pros*: Simplest, maximum freedom.
  - *Cons*: Higher risk of token waste or infinite search loops.
- **Option 2: Conditional Relaxation (Recommended)**: Allow re-retrieval and re-searching when necessary for deeper analysis, verification, or post-modification checks, while keeping the recommendation to cache for general efficiency.
  - *Pros*: Balances analytical depth with token safety/efficiency. Keeps best practices in focus.
  - *Cons*: Slightly longer rule phrasing.

*Decision*: Proceed with Option 2.

## Tasks
- [x] Relax file retrieval and search constraints in [AGENTS.md](file://../../AGENTS.md) <!-- id: task-relax-agents -->
- [x] Relax context efficiency and prompt caching rules in [.agents/rules.md](file://../rules.md) <!-- id: task-relax-rules -->
- [x] Run validation suite `./helper.sh validate` to verify overall compliance <!-- id: task-validate -->

## Acceptance Criteria
- [x] AGENTS.md permits re-retrieving/searching for deeper analysis/verification. <!-- id: crit-agents -->
- [x] `.agents/rules.md` is updated to allow re-querying paths to ensure analytical depth and verification correctness. <!-- id: crit-rules -->
- [x] Workspace validation passes cleanly. <!-- id: crit-validate -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] AGENTS.md <!-- id: audit-target-files -->
  - [x] .agents/rules.md
  - [x] .agents/templates/rules.md.template
- Active module locks:
  - [ ] AGENTS.md <!-- id: lock-AGENTS_md -->
  - [ ] .agents/rules.md <!-- id: lock-rules_md -->
  - [ ] .agents/templates/rules.md.template <!-- id: lock-rules_md_template -->
  - [ ] .agents/scripts/cli/commands/bootstrap <!-- id: lock-bootstrap -->
  - [ ] CHANGELOG.md <!-- id: lock-CHANGELOG_md -->
  - [ ] README.md <!-- id: lock-README_md -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
