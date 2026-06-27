---
id: issue-052
title: "Implement self-learning mechanism and plug-and-play stack adaptation"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Design & Task Specification

## 1. Pre-Implementation Impact Analysis
- **Option A**: Implement stack configuration files inside `.agents/config.json`.
  - *Trade-offs*: High friction, requires developers to manually write files, not truly plug-and-play.
- **Option B (Recommended)**: Auto-detect programming stacks via key project files (e.g. `go.mod`, `Cargo.toml`, `package.json`, `requirements.txt`, etc.) and support any generic stacks without failing the bootstrap execution. Implement a new CLI command `learn` to support self-learning.
  - *Trade-offs*: Low friction, fully automated stack detection, zero configuration needed, scalable.

## 2. Technical Decisions
- **Stack**: Python 3, CLI.
- **Key Modules**:
  - [.agents/scripts/cli/commands/bootstrap.py](file://./.agents/scripts/cli/commands/bootstrap.py)
  - [.agents/scripts/cli/commands/learn.py](file://./.agents/scripts/cli/commands/learn.py)
  - [.agents/scripts/cli/helper.py](file://./.agents/scripts/cli/helper.py)
  - [.agents/memory/lessons-learned.md](file://./.agents/memory/lessons-learned.md)

## 3. Implementation Subtasks
- [x] Implement auto-detection of stacks (Python, Node, PHP, Go, Rust, C#, Java, etc.) and support generic stacks in `bootstrap.py` <!-- id: subtask-bootstrap-detect -->
- [x] Add the `learn` command to `allowed_commands` in `helper.py` <!-- id: subtask-helper-learn -->
- [x] Create the new CLI command module `learn.py` to record developer/agent lessons <!-- id: subtask-learn-cmd -->
- [x] Document the self-learning mechanism and adaptiveness in rules <!-- id: subtask-rules-update -->
- [x] Run validation suite locally <!-- id: subtask-validate -->

## 4. Acceptance Criteria
- [x] The `bootstrap` command works for python/node/php as well as newly detected stacks like Go/Rust/C#
- [x] Running `./helper.sh learn "Lesson content"` appends the lesson to `lessons-learned.md` with date and category
- [x] All checks in `./helper.sh validate` pass successfully
