---
id: issue-237
title: "feat: secure visual dashboard with token auth and host validation"
status: open
assignee: rafaelghif
created_at: 2026-07-10
---

# Issue Details

## Problem Statement
feat: secure visual dashboard with token auth and host validation

## Tasks
- [x] Lock the dashboard module <!-- id: task-lock-dashboard -->
- [x] Propose and capture design and pre-implementation impact analysis <!-- id: task-impact-analysis -->
- [x] Implement dynamic dashboard token generation on startup <!-- id: task-token-generation -->
- [x] Enforce session token validation on visual dashboard HTTP routes <!-- id: task-route-token-check -->
- [x] Enforce Host header validation in is_client_allowed check <!-- id: task-host-header-check -->
- [x] Verify validation checks pass and run tests <!-- id: task-verify-and-test -->

## Acceptance Criteria
- [x] Dashboard python module lock is acquired <!-- id: criteria-dashboard-locked -->
- [x] Token is dynamically generated and printed on dashboard start <!-- id: criteria-token-generated -->
- [x] API routes block requests with invalid/missing token <!-- id: criteria-unauthorized-blocked -->
- [x] DNS Rebinding is blocked by enforcing Host header validation <!-- id: criteria-dns-rebinding-blocked -->
- [x] Local unit tests and validation guard pass successfully <!-- id: criteria-validation-passes -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/scripts/cli/commands/dashboard.py <!-- id: audit-target-files -->
  - [x] .agents/dashboard/app.js <!-- id: audit-target-files-2 -->
  - [x] .agents/tests/test_dashboard.py <!-- id: audit-target-files-3 -->
  - [x] .agents/issues/issue_237.md <!-- id: audit-target-files-4 -->
- Active module locks:
  - [x] dashboard <!-- id: lock-dashboard -->
  - [x] .agents/dashboard/app <!-- id: lock-app -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
