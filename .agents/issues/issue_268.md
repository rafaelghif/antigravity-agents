---
id: issue-268
title: "extend stack auto-reconnaissance to support ruby elixir cpp and swift"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
extend stack auto-reconnaissance to support ruby elixir cpp and swift, ensuring proper framework and unit testing adaptation across all popular programming languages.

## Tasks
- [x] Implement modular stack detectors in `.agents/scripts/recon.py` with framework & unit-test adaptation <!-- id: task-implement-recon -->
- [x] Update `lockfiles` in `.agents/scripts/validate.py` to trigger validations for all popular languages <!-- id: task-update-validate -->
- [x] Write unit tests in `.agents/tests/test_recon.py` and run checks <!-- id: task-write-tests -->
- [x] Verify validations pass and record lessons learned <!-- id: task-verify-finish -->

## Acceptance Criteria
- [x] Stack auto-detection distinguishes C# .NET vs .NET Core and adapts frameworks/tests <!-- id: criteria-dotnet -->
- [x] Stack auto-detection adapts unit-testing (Pest/PHPUnit for PHP, RSpec for Ruby, JUnit for Java, etc.) <!-- id: criteria-multilang -->
- [x] Validations pass and unit tests verify all detectors <!-- id: criteria-validation -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/scripts/recon.py <!-- id: audit-target-files -->
  - [x] .agents/scripts/validate.py
  - [x] .agents/tests/test_recon.py
- Active module locks:
  - [x] .agents/scripts/recon <!-- id: audit-module-locks -->
  - [x] .agents/scripts/validate
  - [x] .agents/tests/test_recon
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
