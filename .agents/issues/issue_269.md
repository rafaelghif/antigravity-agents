---
id: issue-269
title: "recommend stack-compatible architecture designs during auto-reconnaissance"
status: open
assignee: rafaelghif
created_at: 2026-07-11
---

# Issue Details

## Problem Statement
Recommend stack-compatible software architecture styles (e.g. Atomic Design, MVC, Clean Architecture, DDD, Hexagonal) during auto-reconnaissance scan based on primary language stack and detected frameworks.

## Tasks
- [x] Implement architecture recommendations mapping in `.agents/scripts/recon.py` based on language stack and framework combinations <!-- id: task-implement-arch-recon -->
- [x] Update unit tests in `.agents/tests/test_recon.py` to assert correct architecture recommendation strings <!-- id: task-write-arch-tests -->
- [x] Verify validations pass and record lessons learned <!-- id: task-verify-arch-finish -->

## Acceptance Criteria
- [x] React/frontend projects recommend "Atomic Design / Component-driven" <!-- id: criteria-arch-react -->
- [x] .NET, Spring Boot, Quarkus, NestJS, and Vapor projects recommend "Clean Architecture / Hexagonal / DDD" <!-- id: criteria-arch-dotnet-spring -->
- [x] Laravel, Django, Ruby on Rails, and generic PHP/Node/Python projects recommend "MVC" or "Layered (Controller-Service-Repository)" <!-- id: criteria-arch-mvc -->
- [x] WordPress projects recommend "Hooks-based Plugin/Theme Architecture" <!-- id: criteria-arch-wp -->
- [x] Unit tests fully verify these architecture recommendations <!-- id: criteria-arch-tests -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/scripts/recon.py <!-- id: audit-target-files -->
  - [x] .agents/tests/test_recon.py
- Active module locks:
  - [x] .agents/scripts/recon <!-- id: audit-module-locks -->
  - [x] .agents/tests/test_recon
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
