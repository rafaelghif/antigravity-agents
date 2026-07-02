---
id: issue-101
title: "Implement Multi-Language Linting, Graceful Sync Fallbacks, and API Rotation Enhancements"
status: open
assignee: agent-antigravity
created_at: 2026-07-02
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Python 3
- **Architecture**: Validation Guard Extensions, Graceful Failures, API rotation integration
- **Key Modules**:
  - [.agents/scripts/validate.py](file://./.agents/scripts/validate.py)
  - [.agents/scripts/cli/commands/issue.py](file://./.agents/scripts/cli/commands/issue.py)
  - [.agents/scripts/git_api.py](file://./.agents/scripts/git_api.py)

## 2. Implementation Subtasks
- [x] Add multi-language syntax and lint checks (JS/TS, PHP, Python) to `audit_static_linting()` in `validate.py`
- [x] Integrate `.agents/projects.json` `lint_command` execution in static linting audit
- [x] Suppress raw network exception traces in `validate.py` and `git_api.py` on 401/403 API errors, falling back gracefully to local caches
- [x] Implement local-only offline mode for issue sync when unauthorized or offline
- [x] Ensure unit tests cover new multi-language linting and graceful sync fallback behaviors

## 3. Acceptance Criteria
- [x] `validate.py` detects and compiled JS/TS/PHP/Python errors based on modified files
- [x] Validation command runs successfully without throwing raw stack traces when offline or unauthenticated (graceful warning only)
- [x] Unit tests pass successfully
