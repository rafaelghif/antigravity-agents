---
id: issue-043
title: "Rename skills to professional, non-exaggerated enterprise-grade names"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Git CLI, Python 3
- **Architecture**: Restructure custom skills to use standard, professional naming conventions that align with enterprise-grade application development practices.
- **Key Modules**:
  - [.agents/skills/](file://./.agents/skills/)
  - [AGENTS.md](file://./AGENTS.md)
  - [README.md](file://./README.md)

## 2. Implementation Subtasks
- [x] Acquire module locks for `bootstrap` <!-- id: subtask-locks -->
- [x] Rename directories using `git mv`:
  - `world-class-programmer` -> `coding-standards`
  - `tasking` -> `task-management`
  - `adr-writer` -> `adr`
  - `review` -> `code-review` <!-- id: subtask-rename-dirs -->
- [x] Update `SKILL.md` frontmatter metadata inside the renamed skills to align with new names <!-- id: subtask-skill-metadata -->
- [x] Update skill references and descriptions in `AGENTS.md` and `README.md` <!-- id: subtask-references -->
- [x] Add and adjust unit tests to match new skill directory structure <!-- id: subtask-tests -->
- [x] Release locks, run validation, and merge cleanly <!-- id: subtask-finalize -->

## 3. Acceptance Criteria
- [x] Local tests and `./helper.sh validate` pass successfully
- [x] Custom skill directories and names are standard and professional (no exaggerated/lebay naming)
- [x] All references in core project registries (AGENTS.md, README.md, unit tests) are in sync
