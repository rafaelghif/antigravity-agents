# ADR 0002: Strict Workspace-Level Tasking & Commit Validation Gates

## Status
Accepted

## Context
In collaborative development and teamwork settings, agents and human developers often suffer from procedural drift, undocumented changes, and inconsistent commits. We need to enforce a zero-tolerance policy against commits that do not map to verified local tasks, have incomplete checklists, or fail formatting rules.

## Decision
To enforce absolute consistency, we establish three programmatic compliance gates strictly at the workspace level (within the project directory):

1. **Context Alignment Gate (`AGENTS.md`)**: The root-level `AGENTS.md` explicitly lists non-negotiable rules and the working protocol. Since this file is prepended to every prompt, the agent cannot hallucinate or ignore the required task setup steps.
2. **Pre-Commit Hook Validation Guard (`validate.py`)**: Runs on every commit attempt. It ensures:
   - Branch names align with an active issue ID.
   - A local issue specification file exists under `.agents/issues/`.
   - Every single checklist task (`- [ ]`) in the active issue file is completed (`[x]`).
   - No credentials, keys, or forbidden private config files are staged.
3. **Commit-Msg Hook Enforcer (`commit-msg`)**: Validates that all commit messages follow Conventional Commits and explicitly contain the active task/issue ID reference.

## Consequences
- Developers and agents cannot commit code unless a task has been created, mapped on the board, and all of its subtasks are fully completed.
- Eliminates credentials leakage and Git message formatting errors.
- Guarantees that the repository's task board and issue files are always in perfect sync with the Git history.
