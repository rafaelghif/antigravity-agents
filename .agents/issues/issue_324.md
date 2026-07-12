---
id: issue-324
title: "feat: enhance rules to enforce expert senior developer practices and avoid duplicates"
status: closed
assignee: agent-antigravity
created_at: 2026-07-12
---

# Issue Details

## Problem Statement
The user wants to refine the developer rules in `AGENTS.md` and `.agents/rules.md` (and their templates) to ensure the AI behaves like an expert senior developer/software engineer. This includes:
1. Always checking built-in or already installed libraries first to avoid duplicate libraries/dependencies.
2. Optimizing code like a senior developer (most efficient, secure, performant, maintainable, scalable).
3. Ensuring template mapping parity for `.agents/rules.md` (matching `.agents/templates/rules.md.template`).

## Tasks
- [x] Add senior developer personality, library duplicate check, and code optimization rules to `AGENTS.md` §2 Non-negotiable rules. <!-- id: task-agents-rules -->
- [x] Add identical rules to `.agents/rules.md` under §4 Enterprise-Grade Standards and §1 Programming Language & Tools. <!-- id: task-rules-md -->
- [x] Add matching template updates to `.agents/templates/rules.md.template`. <!-- id: task-rules-template -->
- [x] Run validation checks using helper script to verify all tests and rules pass. <!-- id: task-validate-checks -->

## Acceptance Criteria
- [x] `AGENTS.md` has the new rules under §2. <!-- id: crit-agents-rules-added -->
- [x] `.agents/rules.md` has matching rules under §4. <!-- id: crit-rules-md-added -->
- [x] `.agents/templates/rules.md.template` has matching rules. <!-- id: crit-rules-template-added -->
- [x] Validation check passes successfully. <!-- id: crit-validation-passes -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] AGENTS.md <!-- id: audit-target-files -->
  - [x] .agents/rules.md
  - [x] .agents/templates/rules.md.template
- Active module locks:
  - [x] rules <!-- id: audit-module-locks -->
  - [x] core
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
