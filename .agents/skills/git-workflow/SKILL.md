---
name: git-workflow
description: End-to-end Version Control Lifecycle manager (Issue, Branch, PR).
instruction: Strictly handles the end-to-end Version Control Lifecycle (Issue -> Gitea Time Tracking -> Branch -> Atomic Commits -> PR -> Merge & Delete).
requires_core: ">=4.0.0"
---
# Git Workflow Enterprise Skill

## Objective
To autonomously execute the strict Version Control & Collaboration lifecycle as defined in the AAC V4 Core Directive (AGENTS.md). This skill ensures zero deviation from the standard operating procedures.

## Bypass Condition (Quick Mode)
If the user specifies `!quick` or explicitly asks to "skip version control lifecycle", DO NOT create an issue, DO NOT start Gitea time tracking, and DO NOT create a PR.
However:
- Still create a new branch, using the `<prefix>/quick-<slug>` format (e.g., `feature/quick-<slug>`).
- Still make atomic commits with conventional messages.
- Do NOT merge to main without `ask_question` approval.

## Execution Steps

### 1. Issue Creation (External Tracking)
- **Origin Detection**: Check `git remote -v` for origin URL. If `github.com` → GitHub. If `gitea` or `git.[domain]/` → Gitea. If unknown → Use `ask_question`.
- Create a new issue.
- **Title Format**: MUST follow Conventional Commits (e.g., `feat: implement login strategy`).
- **Body**: Brief description of the task requirements.

### 2. Time Tracking Initialization (Gitea-Specific)
- **Mandatory**: If the repository is on Gitea, you MUST start the time tracker for the newly created issue *before* proceeding to code.
- Fallback: Use `tea` CLI if MCP is unavailable. If both are unavailable, PAUSE the workflow, use `ask_question` to notify the user. If user explicitly says "proceed without tracking", document in `.agents/incidents/tracking-override-<date>.md` and proceed. Otherwise, PAUSE.

### 2.5 Unified Planning (Internal Traceability)
- Create a lightweight task checklist inside `.agents/plans/<issue_id>-<slug>.md` (or `<slug>-<date>.md` if `!quick` mode skipped issue creation).
- Format: A simple markdown checklist with sequential subtasks derived from the issue description. Mark tasks as `[x]` during execution.

### 2.7 Context Compaction
- Summarize intermediate tool outputs and reasoning from the planning phase into `.agents/scratch/compaction.md`.
- Drop redundant tokens and preserve only essential variables required for later git commits.

### 3. Branching
- Fetch and checkout the latest `main` (or designated base branch).
- Create a new branch.
- **Prefixes Allowed**: `feature/`, `bugfix/`, `hotfix/`, `chore/`, `refactor/`. If in `!quick` mode, use format `<prefix>/quick-<slug>` (e.g., `feature/quick-<slug>`).

### 4. Code Execution & Atomic Commits
- Make necessary file edits fulfilling the issue requirements.
- **Commit Rules**: Do not bundle everything into one massive commit. Make logical, small commits.
- **Message Format**: `<type>: <description> (Fixes #<issue_id>)`. Use `Fixes #` universally.

### 5. Pull/Merge Request Generation
- Create a PR linking the branch to `main`.
- **Title**: Match the issue title (Conventional Commits).
- **PR Draft Strategy**: If PR has > 500 lines changed → Create as draft. Mark as ready when all checks pass. Draft PRs don't trigger merge gates.
- **Body**: 
  - What changed
  - Why it changed
  - `Fixes #<issue_id>`
  - Test steps

### 5.5 Merge Conflict Protocol
- If a merge conflict occurs, PAUSE. Identify conflicting files via `git diff --name-only`.
- **Lock File Conflicts**: Accept main's version as base. Run `npm install` or `pnpm install` to deduplicate. Verify no new packages were removed (diff check). If removed, escalate to user.
- If binaries (`*.png`, `*.jpg`): Manual resolution required, escalate to user.
- If derived files (`coverage/`): Ignore or remove them and regenerate after merge.
- Analyze source code conflicts and safely resolve. If >3 files conflict, escalate to the user before proceeding.

### 6. Merge & Final Cleanup
- **Merge Gate**: Merging to the base branch is a destructive/high-stakes action. You MUST use the `ask_question` tool to get explicit user approval before executing the merge, unless previously overridden.
- **Merge**: Execute the merge after approval.
- **Time Tracking**: If on Gitea, STOP the issue time tracker.
- **Branch Cleanup**: Delete the branch both locally and remotely to prevent repository bloat.
