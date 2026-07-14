---
id: issue-331
title: "fix: install cryptography dependency in verify workflow"
status: closed
assignee: rafaelghif
created_at: 2026-07-14
---

# Issue Details

## Problem Statement
The GitHub Actions workflow fails during the local unit test execution phase because `cryptography` and other required third-party dependencies are not installed in the runner's Python environment. We need to install the dependencies defined in `requirements.txt` (with caching) prior to executing stack detection, validation, and unit tests.

## Pre-Implementation Impact Analysis
- **Option A (Recommended)**: Enable pip cache in the setup-python step and run `pip install -r requirements.txt` prior to executing checks and tests.
  - *Pros*: Direct, standard, uses existing project-defined dependencies source of truth (`requirements.txt`), implements pip caching for build speed.
  - *Cons*: None.
- **Option B**: Manually pip install individual packages (`cryptography`, `keyring`, `portalocker`) in the workflow inline step.
  - *Pros*: None.
  - *Cons*: High maintenance, duplicate definitions of package versions, prone to version drift.

## Tasks
- [x] Add pip caching and install dependencies in `.github/workflows/verify.yml` <!-- id: task-workflow-dependencies -->

## Acceptance Criteria
- [x] The `test-suite` job in `.github/workflows/verify.yml` contains a step to install dependencies from `requirements.txt` using cached pip packages.
- [x] Local validation script passes successfully.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] `.github/workflows/verify.yml` <!-- id: audit-target-files -->
- Active module locks:
  - [x] `.github/workflows/verify` <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
