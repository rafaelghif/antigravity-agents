---
id: issue-055
title: "Synchronize README.md with CLI commands, monorepo projects, and skills"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Design & Task Specification

## 1. Pre-Implementation Impact Analysis
- **Option A**: Keep README.md as-is.
  - *Trade-offs*: Outdated documentation, increases onboarding friction.
- **Option B (Recommended)**: Synchronize README.md with the newly added CLI commands, monorepo configuration, and custom skills index.
  - *Trade-offs*: Keeps codebase unified and fully professional, zero friction.

## 2. Technical Decisions
- **Stack**: Markdown.
- **Key Modules**:
  - [README.md](file://./README.md)

## 3. Implementation Subtasks
- [x] Add `learn` command description to README.md CLI table <!-- id: subtask-readme-learn-cmd -->
- [x] Document monorepo setup and projects.json configuration <!-- id: subtask-readme-monorepo -->
- [x] Add contract-synchronization skill to directory blueprint map <!-- id: subtask-readme-blueprint -->
- [x] Run validation suite locally <!-- id: subtask-validate -->

## 4. Acceptance Criteria
- [x] The `learn` command is clearly listed in README.md
- [x] Monorepo configuration and `contract-synchronization` are documented
- [x] `./helper.sh validate` passes successfully without errors
