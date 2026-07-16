---
id: issue-350
title: "fix github action test_fetch_github_issues_success failure"
status: closed
assignee: rafaelghif
created_at: 2026-07-16
---

# Issue Details

## Problem Statement
fix github action test_fetch_github_issues_success failure

## Pre-Implementation Impact Analysis
- **Option A (Recommended)**: Patch `git_api.get_service_info` in `test_sync.py` to return mock credentials. It directly maps to the new Gitea/GitHub api structure in `git_api.py`. Low complexity, clean test alignment.
- **Option B**: Modify production code `git_api.py` to fall back to calling mock helper functions. Brittle, introduces dead code paths, and increases cognitive complexity.

## Tasks
- [x] Task 1: Patch `git_api.get_service_info` in `test_sync.py` to return valid mock credentials inside `test_fetch_github_issues_success`. <!-- id: task-1 -->
- [x] Task 2: Run validation check locally using `./helper.sh validate` to verify it passes successfully. <!-- id: task-2 -->

## Acceptance Criteria
- [x] Direct test `test_fetch_github_issues_success` passes locally. <!-- id: crit-1 -->
- [x] Local validation guard passes successfully without failures. <!-- id: crit-2 -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] `.agents/tests/test_sync.py` <!-- id: audit-target-files -->
- Active module locks:
  - [ ] None <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
