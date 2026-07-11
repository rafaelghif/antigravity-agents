---
name: task-management
description: Playbook for capturing design alignment from /grill-me, generating issue specifications, and managing task boards.
---

# Task Management & Design Capture Skill Playbook

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
milestone: "v3.4x"
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

## 2. Synchronizing with the Task Board and Git Branch
Once the issue file is written:
1. Run `python3 .agents/scripts/sync.py` to synchronize any links.
2. The task board (`board.md`) is automatically synchronized with local issues when running `./helper.sh issue sync`. You can also manually add/move the task if needed:
   `- [ ] [Title] (feat/issue-[number]) <!-- id: issue-[number] -->`
3. Add the issue ID (e.g., `- [ ] issue-[number]`) under the corresponding milestone version section in `.agents/memory/milestones.md`.
4. Transition the task to `Doing` before starting work.
5. Create and checkout a new branch for the issue immediately (e.g., `./helper.sh issue checkout issue-[number]`). **NEVER** edit files or commit directly on the `main` or `master` branch.

Note: Task statuses and checkbox states in `board.md` are automatically kept in sync with issue file statuses whenever issues are synchronized, checkout, or closed.
