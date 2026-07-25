---
name: branch-janitor
description: Scans for and safely deletes stale or merged local and remote branches.
instruction: Use when cleaning up the repository, or when the user reports leftover branches after PR merges.
requires_core: ">=4.1.4"
---
# Branch Janitor Skill

## Objective
Eradicate leftover stale branches in both local and remote repositories to keep the project clean, solving the exact issue where agents or users forget to clean up `feature/` and `hotfix/` branches after merging.

## When to Execute
- When explicitly requested by the user to "clean up branches".
- As a fallback if the `git-workflow` skill failed to delete a branch during its PR merge step.

## Execution Steps
1. **Identify Merged Branches**:
   - Run `git fetch --prune` to synchronize with remote.
   - Run `git branch --merged main -r` to identify all remote branches that have been merged into main.
   - Run `git branch --merged main` to identify all local branches that have been merged into main.
2. **Safe Deletion Filter**:
   - MUST ignore `main`, `master`, `develop`, and `staging` branches. Do NOT attempt to delete them.
3. **Execution**:
   - For every target local branch: `git branch -d <branch_name>`
   - For every target remote branch (e.g. `origin/feature/abc`): `git push origin --delete feature/abc`
4. **Verification**:
   - Run `git ls-remote --heads origin` to verify no target branches remain.
   - Update `.agents/brain/audit.jsonl` with the branches that were deleted.
