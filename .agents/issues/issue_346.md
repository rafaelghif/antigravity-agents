---
id: issue-346
title: "refactor: upgrade agent core codebase to enterprise-grade standards"
status: open
assignee: agent-antigravity
created_at: 2026-07-16
---

# Design & Task Specification

## Technical Decisions
We will refactor the agent core commands and services to use enterprise-grade logging and subprocess execution layers, replacing scattered raw `print` outputs and unmonitored `subprocess.run` calls.
- **`core/logger.py`**: A unified, structured logger supporting standard levels (`debug`, `info`, `warn`, `error`, `success`), color outputs, and optional JSON/structured logs for telemetry.
- **`core/executor.py`**: A defensive shell runner wrapper around `subprocess` that logs inputs/outputs, tracks runtime duration (telemetry), and sanitizes calls to block shell/argument injections.

## Tasks
- [x] Create core logging utility `.agents/scripts/core/logger.py` <!-- id: task-create-logger -->
- [x] Create core shell executor utility `.agents/scripts/core/executor.py` <!-- id: task-create-executor -->
- [x] Integrate logger and executor into lock service `lock_service.py` <!-- id: task-integrate-lock-service -->
- [x] Integrate logger and executor into token service `token_service.py` <!-- id: task-integrate-token-service -->
- [x] Integrate logger and executor into issue service `issue_service.py` <!-- id: task-integrate-issue-service -->
- [x] Write unit tests for logger and executor in `.agents/tests/test_core_utils.py` <!-- id: task-write-tests -->
- [x] Run sync and validation checks to verify correctness <!-- id: task-sync-validate -->

## Acceptance Criteria
- [x] Logger and executor execute and validate output correctly without shell injections <!-- id: ac-security -->
- [x] Existing codebase passes all validations and tests successfully <!-- id: ac-tests-pass -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] `.agents/scripts/core/logger.py` <!-- id: target-logger -->
  - [x] `.agents/scripts/core/executor.py` <!-- id: target-executor -->
  - [x] `.agents/scripts/cli/commands/services/lock_service.py` <!-- id: target-lock-service -->
  - [x] `.agents/scripts/cli/commands/services/token_service.py` <!-- id: target-token-service -->
  - [x] `.agents/scripts/cli/commands/services/issue_service.py` <!-- id: target-issue-service -->
  - [x] `.agents/tests/test_core_utils.py` <!-- id: target-tests -->
- Active module locks:
  - [x] lock_service.py locked <!-- id: audit-lock-service -->
  - [x] token_service.py locked <!-- id: audit-token-service -->
  - [x] issue_service.py locked <!-- id: audit-issue-service -->
  - [x] profile.py locked <!-- id: audit-profile -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
