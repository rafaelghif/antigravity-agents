---
name: devops-manager
description: Version Control Lifecycle manager, branch hygiene janitor, and CI/CD local runner specialist. Triggers when creating issues, branching, submitting PRs, cleaning merged branches, or simulating GitHub Actions locally.
requires_core: ">=4.2.0"
---
# DevOps Manager Skill

## Objective
Seamless management of Git version control lifecycles, branch hygiene, and CI/CD automation pipelines.

## 1. Version Control Lifecycle (Git Workflow)
- **Branching & Worktree Protocol**: Create `<prefix>/<slug>` (`feature/`, `bugfix/`, `hotfix/`, `chore/`, `refactor/`). For high-risk operations, use `git worktree add ../<branch-name> -b <branch-name> origin/main` to avoid corrupting workspace state.
- **Atomic Commits**: Logical conventional commits (`feat: ...`, `fix: ...`).
- **Platform-Specific Issue Linking**:
  - GitHub: `<type>: <description> (Fixes #<id>)`
  - Gitea: `<type>: <description> (Closes #<id>)`
- **PR Generation & Draft Strategy**: If PR changes $> 500$ lines, submit as Draft PR first until tests pass. Include summary, rationale, `Fixes #<id>`, and reproduction test steps.
- **Merge Conflict Resolution**: If merge conflicts occur, identify files via `git diff --name-only`. For lockfile conflicts (`package-lock.json`), accept main base and rerun `npm install`. For binary file conflicts, escalate to user immediately.
- **Merge Gate Approval**: Merging to the base branch REQUIRES explicit user approval via `ask_question`.


## 2. Branch Hygiene (Branch Janitor)
- Scan for merged or stale local/remote branches.
- Safely delete merged branches (`git branch -d`, `git push origin --delete`) to maintain repository hygiene.

## 3. Local CI/CD Pipeline Simulation
- Use `act` CLI or local runners to simulate GitHub Actions workflows locally before pushing.
- Catch environment or pipeline syntax errors prior to remote deployment.
