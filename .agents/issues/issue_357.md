---
id: issue-357
title: "upgrade fallback version references to v3.119.0"
status: open
assignee: rafaelghif
created_at: 2026-07-16
---

# Issue Details

## Problem Statement
upgrade fallback version references to v3.119.0

## Pre-Implementation Impact Analysis
- **Option A (Recommended)**: Update dashboard version fallbacks to `3.119.0` to maintain consistency across the entire framework.
- **Option B**: Skip updates, leaving stale `v2.109.0` fallbacks.

## Tasks
- [x] Task 1: Update dashboard `index.html` fallback to `v3.119.0`. <!-- id: task-html -->
- [x] Task 2: Update `app.js` fallback to `3.119.0`. <!-- id: task-js -->
- [x] Task 3: Update `dashboard.py` fallback to `3.119.0`. <!-- id: task-py -->

## Acceptance Criteria
- [x] All fallback version references match `3.119.0`. <!-- id: ac-version-match -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] `.agents/dashboard/index.html` <!-- id: target-html -->
  - [x] `.agents/dashboard/app.js` <!-- id: target-js -->
  - [x] `.agents/scripts/cli/commands/dashboard.py` <!-- id: target-py -->
- Active module locks:
  - [x] `dashboard` <!-- id: lock-dashboard -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
