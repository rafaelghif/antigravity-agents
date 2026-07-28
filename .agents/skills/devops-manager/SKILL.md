---
name: devops-manager
description: Version Control Lifecycle manager, branch hygiene janitor, and CI/CD local runner specialist. Triggers when creating issues, branching, submitting PRs, cleaning merged branches, or simulating GitHub Actions locally.
requires_core: ">=4.3.0"
---
# DevOps Manager Skill

## Objective
Seamless management of Git version control lifecycles, branch hygiene, and CI/CD automation pipelines.

## 1. Version Control Lifecycle (Git Workflow)
- **Branching per Task Plan**: Automatically derive branch names from active Task Plan slug (e.g., `task/<task-slug>`). For high-risk operations, use `git worktree add ../<branch-name> -b <branch-name> origin/main` to avoid corrupting workspace state.

- **Atomic Commits**: Logical conventional commits (`feat: ...`, `fix: ...`).
- **Platform-Specific Issue Linking**:
  - GitHub: `<type>: <description> (Fixes #<id>)`
  - Gitea: `<type>: <description> (Closes #<id>)`
- **PR Generation & Draft Strategy**: If PR changes $> 500$ lines, submit as Draft PR first until tests pass. Include summary, rationale, `Fixes #<id>`, and reproduction test steps.
- **Git Merge Conflict Resolution Protocol**:
  - Before running final empirical test verification, execute `git rebase main` to ensure the task branch is up-to-date with base main.
  - If merge conflicts occur (`<<<<<<< HEAD`), identify conflicting files via `git diff --name-only`.
  - **Conflict Boundary**: For lockfile conflicts (`package-lock.json`), accept main base and rerun `npm install`. For source code conflicts, resolve using AST/SOLID rules and NEVER leave conflict markers in code. For unresolvable binary conflicts, escalate immediately via `ask_question`.
- **Merge Gate Approval**: Merging to the base branch REQUIRES explicit user approval via `ask_question`.



## 2. Branch Hygiene (Branch Janitor)
- Scan for merged or stale local/remote branches.
- Safely delete merged branches (`git branch -d`, `git push origin --delete`) to maintain repository hygiene.

## 3. Local CI/CD Pipeline Simulation
- Use `act` CLI or local runners to simulate GitHub Actions workflows locally before pushing.
- Catch environment or pipeline syntax errors prior to remote deployment.
