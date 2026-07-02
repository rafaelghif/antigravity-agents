---
id: issue-133
title: "Implement automatic upgrade check for CLI commands"
status: open
assignee: agent-antigravity
created_at: 2026-07-02
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Python 3 (standard libraries: `threading`, `time`, `json`, `subprocess`).
- **Architecture**: Async background thread auto-updater that triggers at CLI command exit. Checks if the active branch is a base branch, checks if git core paths are clean, fetches remote tracking branches (falling back to user's remote origin or core source repo), and checkouts core files if remote contains updates.
- **Key Modules**:
  - [.agents/scripts/cli/commands/upgrade.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/upgrade.py)
  - [.agents/scripts/cli/helper.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/helper.py)

### Pre-Implementation Impact Analysis
- **Option A (Recommended)**: Async background execution gated by a 30-minute rate limit, working tree clean check, and branch verification.
  - *Trade-off*: Safest developer experience. No manual intervention required. Performance impact is completely avoided via thread isolation and rate-limiting.
- **Option B**: Blocking auto-upgrade check on every execution.
  - *Trade-off*: Simple but highly frustrating due to slow network latency on every CLI run.

## 2. Implementation Subtasks
- [x] Subtask 1: Implement `check_and_run_auto_upgrade` inside `upgrade.py`.
- [x] Subtask 2: Integrate the async thread runner in `helper.py`'s exit lifecycle hook.
- [x] Subtask 3: Add unit tests in `test_upgrade.py` to cover check conditions, mock clean/dirty status, and rate-limiting cache.
- [x] Subtask 4: Verify the local validation guard passes.

## 3. Acceptance Criteria
- [x] Auto-upgrade check triggers only once every 30 minutes (cache rate limit).
- [x] If local files are dirty, auto-upgrade exits immediately without altering workspace files.
- [x] Running a normal command automatically fetches and notifies the user if an upgrade was applied successfully.
- [x] Unit tests for the auto-upgrade check succeed.
