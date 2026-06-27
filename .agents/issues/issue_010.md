---
id: issue-010
title: "Implement V2 Python CLI and bootstrap logic"
status: open
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
- [ ] Create `.agents/scripts/cli/helper.py` entry parser.
- [ ] Implement `.agents/scripts/cli/commands/lock.py` for locking modules.
- [ ] Implement `.agents/scripts/cli/commands/validate.py` (importing from our validation script).
- [ ] Implement `.agents/scripts/cli/commands/sync.py` (importing from our sync script).
- [ ] Implement `.agents/scripts/cli/commands/issue.py` (issue lifecycle: create, list, checkout, close).
- [ ] Implement `.agents/scripts/cli/commands/commit.py` (git profiles round-robin config switching).
- [ ] Create wrapper scripts `helper.sh` and `helper.ps1` at workspace root.

## 3. Acceptance Criteria
- [ ] Running `./helper.sh validate` passes validation tests.
- [ ] Running `./helper.sh issue list` displays all active issues.
- [ ] Commits made via `./helper.sh commit` automatically swap git profile configurations.
