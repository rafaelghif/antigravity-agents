---
id: issue-099
title: "Implement Robust Self-Learning and Auto-Sync Guard Integration"
status: open
assignee: agent-antigravity
created_at: 2026-07-02
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Python 3
- **Architecture**: CLI & Hook Integration, Validation Guard Enhancement
- **Key Modules**:
  - [.agents/scripts/validate.py](file://./.agents/scripts/validate.py)
  - [.agents/scripts/cli/commands/learn.py](file://./.agents/scripts/cli/commands/learn.py)
  - [.agents/scripts/cli/commands/context.py](file://./.agents/scripts/cli/commands/context.py)
  - [AGENTS.md](file://./AGENTS.md)

## 2. Implementation Subtasks
- [x] Enhance validation guard in `.agents/scripts/validate.py` to auto-sync workspace elements (skills, ADRs, rules)
- [x] Enhance learn command in `.agents/scripts/cli/commands/learn.py` to extract lessons in non-interactive environments (commits & diffs)
- [x] Enhance context command in `.agents/scripts/cli/commands/context.py` to inject synthesized rules into active context
- [x] Update `AGENTS.md` to require reading `rules.md` in the Compliance Audit non-negotiable rule
- [x] Write/verify unit tests for the enhanced learn, context, and validate logic

## 3. Acceptance Criteria
- [x] Validation guard auto-syncs without manual intervention
- [x] Learn command successfully auto-extracts lessons when non-interactive
- [x] Context optimizer injects rules from `rules.md` into `active_context.md`
- [x] `validate` command and test suite pass successfully
