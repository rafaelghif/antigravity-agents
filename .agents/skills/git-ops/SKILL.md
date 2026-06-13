---
name: git-ops
description: Manages local Git branches and executes version control flows enforcing the strict Conventional Commits specification.
---

# Git Operations Skill

## 1. Input Specification
- **Operation Scope**: Feature development, bug fixing, refactoring, or infrastructure adjustments.
- **Changed Files List**: Selected list of files modified during the current subtask.
- **Target Branch**: Typically a feature branch branched off `main`/`master`.

## 2. Operational Procedures & Checklist
1. **Branch Hygiene & Naming Check**:
   - Ensure you are working on the user's checked-out feature branch.
   - You must NOT create, delete, switch, merge, push, or pull branches.
   - If the active branch is `main` or `master`, or if a branch operation is required, halt and instruct the user to handle the git branch operation.
2. **Pre-Staging Verification**:
   - Run compilation and tests locally (e.g. `npm run build` / `npm run test` or language-equivalent tools) before staging any files.
3. **Secret Scan Check**:
   - Ensure you are not staging `.env`, `.env.local`, credentials files, or private keys.
   - Run `git status` to see untracked and modified files.
4. **Selective Staging**:
   - Stage files individually rather than staging all: `git add <path/to/modified/file>`.
   - Run `git diff --cached` to inspect lines added and verify that no debugging statements or temporary passwords are being committed.
5. **Commit Assembly**:
   - Compose the message strictly matching: `type(scope): description`
     - **Types**: `feat` (new features), `fix` (bug fixes), `refactor` (code restructuring), `chore` (infra, build tools, dependency adjustments, memory updates).
     - **Scopes**: Use the project-specific module name or workspace directory (e.g. `backend`, `frontend`, `infra`, `auth`, `shared`, `db`).
     - *Example*: `fix(frontend): adjust asset detail layout overlay overflow`
6. **Local Commit Verification**:
   - Verify that the commit is successfully completed locally.
   - Inform the user that the changes have been committed, and let them handle pushing to the remote origin.

## 3. Decision Matrix
- **Are there remote changes that need to be pulled?**
   - **YES**: Halt and ask the user to pull the updates for you.
- **Did a file containing private credentials get staged/committed?**
   - **YES**: Instantly stop and undo: `git reset HEAD~1` (if committed) or `git reset HEAD <file>` (if staged). Move keys into `.env` and add the filename to `.gitignore`.

## 4. Error Mitigation Tree
- **Detached HEAD State**:
   - *Mitigation*: Run `git checkout <branch-name>` immediately to re-anchor on the active tracking branch.
- **Accidental commit to `main` branch**:
   - *Mitigation*: Run `git branch temp-branch`, reset main back to remote state: `git reset --hard origin/main`, then switch back: `git checkout temp-branch`.

## 5. Output Protocol
Update the project's active memory ledger (`.agents/memory.md`) under the Git/version control section with the active branch, last commit hash, and target PR status.
