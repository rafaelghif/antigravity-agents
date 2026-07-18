---
name: task-management
description: Playbook for capturing design alignment, generating remote Git issues via MCP, and managing task boards.
---

# Task Management & Design Capture Skill Playbook

Use this playbook immediately after a `/grill-me` design alignment session to capture decisions and scaffold tasks.

## 1. Remote-First Issue Creation (MCP)
After aligning with the user on technical designs, the agent MUST create a new issue directly on the remote Git tracker (GitHub/Gitea) using the corresponding MCP tool (e.g., `create_issue`). 
- **DO NOT** create local markdown files in `.agents/issues/` unless the MCP server is disabled or you are explicitly in offline mode.
- In the issue body, clearly define:
  1. Technical Decisions (Stack, Architecture, Key Modules)
  2. Implementation Subtasks
  3. Acceptance Criteria

## 2. Closing Issues via Git Conventional Messages
When creating a Pull Request (PR) via MCP or when writing commit messages for the final PR, you MUST include `Fixes #<github_number>` in the PR body or commit message. This ensures the remote tracker automatically closes the issue when the PR is merged.

## 3. Synchronizing with the Task Board and Git Branch
Once the remote issue is created:
1. Add the task manually to `.agents/tasks/board.md` under the `Todo` or `Doing` section:
   `- [ ] [Title] (feat/issue-[number]) <!-- id: issue-[number] -->`
2. Add the issue ID (e.g., `- [ ] issue-[number]`) under the corresponding milestone version section in `.agents/memory/milestones.md`.
3. Create and checkout a new branch for the issue immediately (e.g., `git checkout -b feat/issue-[number]-slug` or using `./helper.sh issue checkout`). Enforce Epic-Task branching: branch off the current active epic branch (if applicable), and **NEVER** edit files or commit directly on the `main` or `master` branch.

## 4. Offline Fallback (Only if MCP is disabled)
If and ONLY if you are in offline mode, capture the design into a new markdown file under `.agents/issues/issue_[id].md` using this template:
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
[... Insert Technical Decisions, Subtasks, and Acceptance Criteria ...]
```
*(If offline, you must manually run `./helper.sh issue close <id>` when finished instead of relying on PR auto-close).*

## 5. Session Resumption (Handling Account Switches)
When a user returns to a workspace after switching accounts or starting a fresh conversation session, they may issue a generic command like "continue", "resume", or "lanjutkan". 
1. **ALWAYS** check `.agents/tasks/board.md` for active tasks in the `Doing` column FIRST.
2. If an active task exists, do NOT create a new task or issue.
3. Immediately checkout that issue's branch.
4. Run `./helper.sh context optimize` and read `.agents/state/active_context.md` to perfectly reload the state, uncommitted changes, and active checklist.
