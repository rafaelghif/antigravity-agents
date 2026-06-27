---
id: issue-010
title: "Implement V2 Python CLI and bootstrap logic"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Design & Task Specification: V2 Python CLI

This issue specifies the modular implementation of the Python CLI suite and bootstrap logic.

## 1. Technical Decisions

### CLI Structure
- **Entry point**: `.agents/scripts/cli/helper.py`
- **Commands Directory**: `.agents/scripts/cli/commands/`
  - `lock.py`: Manages transient module locks (stores in `.agents/locks.json`).
  - `validate.py`: Integrates workspace validation (points to `.agents/scripts/validate.py` or contains it).
  - `sync.py`: Invokes context map synchronization.
  - `issue.py`: Handles `create`, `list`, `checkout`, `close` for local issues.
  - `commit.py`: Switches Git email and name configurations from `.agents/git_profiles.json` before committing.

### Wrappers
- `helper.sh` (POSIX) and `helper.ps1` (Windows) in root acting as outer wrappers calling `python3 .agents/scripts/cli/helper.py`.

## 2. Implementation Subtasks
- [x] Create `.agents/scripts/cli/helper.py` entry parser.
- [x] Implement `.agents/scripts/cli/commands/lock.py` for locking modules.
- [x] Implement `.agents/scripts/cli/commands/validate.py` (importing from our validation script).
- [x] Implement `.agents/scripts/cli/commands/sync.py` (importing from our sync script).
- [x] Implement `.agents/scripts/cli/commands/issue.py` (issue lifecycle: create, list, checkout, close).
- [x] Implement `.agents/scripts/cli/commands/commit.py` (git profiles round-robin config switching).
- [x] Create wrapper scripts `helper.sh` and `helper.ps1` at workspace root.

## 3. Acceptance Criteria
- [x] Running `./helper.sh validate` passes validation tests.
- [x] Running `./helper.sh issue list` displays all active issues.
- [x] Commits made via `./helper.sh commit` automatically swap git profile configurations.
