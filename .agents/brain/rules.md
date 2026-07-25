# Agent Rules Ledger

*This file is automatically updated by the `/learn` command. It stores persisted solutions and project-specific invariants.*

## Lessons Learned

- **Branch Cleanup Verification**: Never assume a branch only exists locally. After merging, ALWAYS run `git ls-remote --heads origin` to verify if stale branches (`hotfix/*`, `feature/*`) are left on the remote server. Use `git push origin --delete <branch>` to ensure the production remote remains clean.
