# Agent Rules Ledger

*Persisted solutions, project invariants, and baseline coding standards.*

## 1. Project Invariants & Coding Standards
- **Conventional Commits**: All commit messages MUST follow Conventional Commits specification (e.g. `feat: ...`, `fix: ...`, `chore: ...`).
- **Platform Issue Linking**: Use `Fixes #<id>` for GitHub and `Closes #<id>` for Gitea issues.
- **Code Quality**: Enforce DRY, SOLID, and explicit type checking across TypeScript/Python codebase.
- **Zero Secrets in Code**: Secrets and API tokens MUST be loaded via environment variables (`process.env` / `os.environ`).
- **Mandatory Runtime Verification**: Always verify code edits with project build/test scripts (`npm test`, `pytest`, `cargo test`) before completion.

