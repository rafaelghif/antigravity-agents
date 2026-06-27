---
id: issue-050
title: "Establish Testing and CI-CD playbooks and Refactor existing skills"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Design & Task Specification

## 1. Pre-Implementation Impact Analysis
- **Option A**: Highly detailed, platform-specific playbooks with copy-pasteable configuration files.
  - *Trade-offs*: Easy to copy-paste initially, but high maintenance overhead and high prompt token cost.
- **Option B (Recommended)**: Modular, design-pattern-focused checklists with minimal examples.
  - *Trade-offs*: Durable, low-maintenance, lower token usage, project-agnostic. Adheres to AAC DRY rules.

## 2. Technical Decisions
- **Stack**: Markdown documentation for agent skills.
- **Architecture**: Expand the custom skills directory by adding modular `testing` and `ci-cd` skill playbooks, while refactoring `coding-standards` and `security-audit`.
- **Key Modules**:
  - [.agents/skills/testing/SKILL.md](file://./.agents/skills/testing/SKILL.md)
  - [.agents/skills/ci-cd/SKILL.md](file://./.agents/skills/ci-cd/SKILL.md)
  - [.agents/skills/coding-standards/SKILL.md](file://./.agents/skills/coding-standards/SKILL.md)
  - [.agents/skills/security-audit/SKILL.md](file://./.agents/skills/security-audit/SKILL.md)

## 3. Implementation Subtasks
- [x] Create `testing/SKILL.md` covering unit, integration, and E2E patterns <!-- id: subtask-testing-skill -->
- [x] Create `ci-cd/SKILL.md` covering linting, test, build, and caching configuration <!-- id: subtask-ci-cd-skill -->
- [x] Refactor `coding-standards/SKILL.md` to add guidelines for type annotations and code reviews <!-- id: subtask-coding-refactor -->
- [x] Refactor `security-audit/SKILL.md` to add guidelines for static analyses and dependency pinning <!-- id: subtask-security-refactor -->
- [x] Run validation suite locally <!-- id: subtask-validate -->

## 4. Acceptance Criteria
- [x] All new and updated skill playbooks contain valid YAML frontmatter and register properly
- [x] `./helper.sh validate` passes successfully without errors
- [x] All files are linked using absolute file URLs as required by communication standards
