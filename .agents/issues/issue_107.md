---
id: issue-107
title: "Implement Proactive Private File Scan and Git Branch Type Enforcer"
status: closed
assignee: agent-antigravity
created_at: 2026-07-02
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Python 3
- **Architecture**: Workspace integrity and SemVer protection
- **Key Modules**:
  - [validate.py](file://./.agents/scripts/validate.py)

## 2. Implementation Subtasks
- [x] Add filesystem scanning for unignored private/sensitive files (`.env*`, `git_profiles.json`, `locks.json`) to `audit_secrets_and_ignored_files`
- [x] Add Branch Type Enforcer to `audit_git_branch_alignment` to prevent type mismatches between git branch prefix (`feat/`, `fix/`, `chore/`) and commit types
- [x] Verify validation and unit tests pass successfully

## 3. Acceptance Criteria
- [x] Validation fails if any `.env` file exists in the repository but is not ignored in `.gitignore` or `.antigravityignore`
- [x] Validation fails if branch prefix is `fix/` but a `feat:` commit is found
- [x] Validation fails if branch prefix is `feat/` but no `feat:` commit is found (if commits exist)
- [x] Validation fails if branch prefix is `chore/` but a `feat:` or `fix:` commit is found
- [x] All unit tests pass successfully
