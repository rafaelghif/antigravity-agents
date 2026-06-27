---
name: tasking
description: Playbook for capturing design alignment from /grill-me, generating issue specifications, and managing task boards.
---

# Tasking & Design Capture Skill Playbook

Use this playbook immediately after a `/grill-me` design alignment session to capture decisions and scaffold tasks.

## 1. Capturing Design Alignment
After aligning with the user on technical designs, the agent MUST capture the decisions into a new issue markdown file under `.agents/issues/issue_[id].md`.

### Issue Document Template
Every design capture file must follow this schema:
```markdown
---
id: issue-[number]
title: "Clear descriptive title"
status: open
assignee: agent-antigravity
created_at: [current-date]
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: [Target languages/frameworks]
- **Architecture**: [Blueprints or design patterns applied]
- **Key Modules**: [Files to create or edit]

## 2. Implementation Subtasks
- [ ] Subtask A (e.g. Write tests)
- [ ] Subtask B (e.g. Write business logic)
- [ ] Subtask C (e.g. Validate output)

## 3. Acceptance Criteria
- [ ] Criterion 1 (e.g. Passes pre-commit checks)
- [ ] Criterion 2 (e.g. Tests cover all endpoints)
```

## 2. Synchronizing with the Task Board
Once the issue file is written:
1. Run `python3 .agents/scripts/sync.py` to synchronize any links.
2. Open `.agents/tasks/board.md` and add the task referencing the issue:
   `- [ ] [Title] (feat/issue-[number]) <!-- id: issue-[number] -->`
3. Transition the task to `Doing` before starting work.
