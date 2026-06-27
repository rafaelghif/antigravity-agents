---
id: issue-045
title: "Enforce prompt-level loop guard to prevent agent infinite loops"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Prompt Engineering, Markdown Configuration
- **Architecture**: Enforce a strict non-negotiable loop guard policy in the core agent rules (`AGENTS.md`) and diagnostic playbooks (`debugging/SKILL.md`) to guide LLM behavior.
- **Key Modules**:
  - [AGENTS.md](file://./AGENTS.md)
  - [.agents/skills/debugging/SKILL.md](file://./.agents/skills/debugging/SKILL.md)

## 2. Implementation Subtasks
- [x] Acquire module locks for `bootstrap` <!-- id: subtask-locks -->
- [x] Append a non-negotiable loop guard rule to the rules list in `AGENTS.md` <!-- id: subtask-agents-rule -->
- [x] Update `debugging/SKILL.md` to add step-by-step guidelines for recognizing and resolving deadlocks or infinite retry loops <!-- id: subtask-debugging-skill -->
- [x] Run validation, release locks, and merge cleanly <!-- id: subtask-finalize -->

## 3. Acceptance Criteria
- [x] Local tests and `./helper.sh validate` pass successfully
- [x] A clear loop-guard rule exists in `AGENTS.md` instructing the agent to halt after 3 repeated attempts without progress
