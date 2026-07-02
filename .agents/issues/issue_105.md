---
id: issue-105
title: "Implement Strict Task Splitting and Context Insulation Protocols in Working Guidelines"
status: closed
assignee: agent-antigravity
created_at: 2026-07-02
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: System configurations
- **Architecture**: Enforced agent task splitting and context insulation
- **Key Modules**:
  - [AGENTS.md](file://./AGENTS.md)
  - [.agents/rules.md](file://./.agents/rules.md)

## 2. Implementation Subtasks
- [x] Add strict Task Splitting, Context Insulation, and Context Pruning rules to `AGENTS.md` Working Protocol
- [x] Add corresponding instructions to `.agents/rules.md`
- [x] Lock `bootstrap` and update task board

## 3. Acceptance Criteria
- [x] Working protocol requires atomic subtask splitting and validation per subtask
- [x] Context optimization is mandatory between subtasks to prevent hallucination
- [x] Unit tests pass successfully
