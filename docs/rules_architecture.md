# Core Rules & Architecture Purity

This document outlines the strict validation rules, decoupled architectural boundaries, and guidelines enforced on AI software engineering agents working in this repository.

---

## 1. Core Rules for the Agent

Antigravity Workspace enforces these key rules on AI agents:
- **Strict Bootstrapping sequence**: At startup, the agent MUST read `AGENTS.md` ➔ `rules/project_rules.md` ➔ `schema.md` ➔ `memory.md` in order. No other tools or files may be touched prior to this.
- **Git-Backed Memory Sync**: All schemas, ADRs, dynamic workflows, and memory files under `.agents/` (except `.agents/locks/`) MUST be committed to Git. The agent will run verification checks on startup to ensure your local clone is not behind upstream (`origin`).
- **No Agent Git Push/Pull**: The agent is **forbidden** from running remote operations like `git pull`, `git push`, or changing branches. The user must fetch/pull updates before starting work.
- **Discussion Traceability**: All `/grill-me` or design discussion outcomes are immediately saved to `.agents/workflows/task_<task_name>.md`. When feature branches are merged, running `helper.sh archive` moves these files to `.agents/archive/sprint_<branch>/` to keep active workspace clean.
- **Real-Time Schema & Dependency Sync**: Database model or API changes must immediately update `.agents/schemas/` and the main `.agents/schema.md` index before coding starts. Library dependencies must update `.agents/rules/project_rules.md` and package manager configs (`package.json`, etc.) immediately.
- **Token Optimization (.antigravityignore)**: Agents strictly adhere to `.antigravityignore` patterns, preventing costly crawls through dependencies, logs, binaries, or build directories.
- **Hardcoded Secret Scan**: The agent cannot commit code if passwords, keys, or API tokens are detected in the workspace (scanned via `validate.sh`).
- **Handover Relayed Context**: Before finishing a turn or switching accounts, the agent writes the current status and next action items in `memory.md` under `## 3. Relayed Context & Handover Notes`, ensuring the next agent picks up immediately without token waste.

---

## 2. Decoupled Architecture Boundaries

To ensure 10-year codebase maintainability:
- **Domain Decoupling**: Core business logic (entities, domains, and use-cases) must remain completely independent of server frameworks (e.g. Next.js, FastAPI, Gin), database drivers, or ORM clients.
- **Adapter Segregation**: All database, API, and environment operations must reside in isolated adapter packages, which map external schemas to internal domain logic.
