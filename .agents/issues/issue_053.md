---
id: issue-053
title: "Implement monorepo multi-project support and API contract synchronization"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Design & Task Specification

## 1. Pre-Implementation Impact Analysis
- **Option A**: Implement custom verification commands inside user-specific helper scripts.
  - *Trade-offs*: Fragile, configuration is scattered, doesn't validate automatically on every commit/close.
- **Option B (Recommended)**: Establish `.agents/projects.json` for mapping multiple sub-projects, integrate multi-project test execution in `.agents/scripts/validate.py`, and create a `contract-synchronization` custom skill playbook.
  - *Trade-offs*: Modular, centralizes configuration, automates cross-project contract/test verification during local validation gates, zero friction.

## 2. Technical Decisions
- **Stack**: Python 3, CLI, markdown skills.
- **Key Modules**:
  - [.agents/scripts/validate.py](file://./.agents/scripts/validate.py)
  - [.agents/skills/contract-synchronization/SKILL.md](file://./.agents/skills/contract-synchronization/SKILL.md)
  - [.agents/projects.json](file://./.agents/projects.json)

## 3. Implementation Subtasks
- [x] Create `contract-synchronization` skill directory and playbook `SKILL.md` defining backend/frontend API schemas, client codegen, and contract verification <!-- id: subtask-create-sync-skill -->
- [x] Refactor `.agents/scripts/validate.py` to support scanning and running `test_command` for all sub-projects listed in `.agents/projects.json` <!-- id: subtask-validate-multiproject -->
- [x] Create `.agents/projects.json` schema blueprint and register it in `.agents/schema.md` <!-- id: subtask-register-schema -->
- [x] Run validation suite locally <!-- id: subtask-validate -->

## 4. Acceptance Criteria
- [x] The `contract-synchronization` skill registers successfully and links properly
- [x] Validation suite detects `.agents/projects.json` and runs sub-project tests
- [x] `./helper.sh validate` passes successfully without errors
