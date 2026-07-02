---
id: issue-100
title: "Ignore active_context.md in Git and Antigravity ignore configurations"
status: closed
assignee: agent-antigravity
created_at: 2026-07-02
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Standard configurations
- **Architecture**: Workspace Ignore Hardening
- **Key Modules**:
  - [.gitignore](file://./.gitignore)
  - [.antigravityignore](file://./.antigravityignore)

## 2. Implementation Subtasks
- [x] Add `.agents/active_context.md` to `.gitignore`
- [x] Add `.agents/active_context.md` to `.antigravityignore`
- [x] Verify that `.agents/active_context.md` is ignored by Git

## 3. Acceptance Criteria
- [x] Git check-ignore reports `.agents/active_context.md` is ignored
- [x] Validation command and test suite pass successfully
