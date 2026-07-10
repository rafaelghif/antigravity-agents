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
- [ ] Implement dynamic dashboard token generation on startup <!-- id: task-token-generation -->
- [ ] Enforce session token validation on visual dashboard HTTP routes <!-- id: task-route-token-check -->
- [ ] Enforce Host header validation in is_client_allowed check <!-- id: task-host-header-check -->
- [ ] Verify validation checks pass and run tests <!-- id: task-verify-and-test -->

## Acceptance Criteria
- [x] Dashboard python module lock is acquired <!-- id: criteria-dashboard-locked -->
- [ ] Token is dynamically generated and printed on dashboard start <!-- id: criteria-token-generated -->
- [ ] API routes block requests with invalid/missing token <!-- id: criteria-unauthorized-blocked -->
- [ ] DNS Rebinding is blocked by enforcing Host header validation <!-- id: criteria-dns-rebinding-blocked -->
- [ ] Local unit tests and validation guard pass successfully <!-- id: criteria-validation-passes -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [ ] .agents/scripts/cli/commands/dashboard.py <!-- id: audit-target-files -->
  - [ ] .agents/issues/issue_237.md <!-- id: audit-target-files-2 -->
- Active module locks:
  - [ ] dashboard <!-- id: lock-dashboard -->
- Non-negotiable rules checked:
  - [ ] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [ ] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [ ] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
