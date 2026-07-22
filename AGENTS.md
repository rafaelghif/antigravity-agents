# AGENTS.md — Antigravity Agent Core (AAC) V3

> Budget: < 150 lines. Be terse but uncompromisingly strict on guardrails.

## 1. Project
- **Product:** test-proj
- **Version:** 4.0.1
- **Stack:** Python 3, Docker
- **Layout:** CLI scripts, `.agents/skills/` (playbooks), `.agents/workflows/`, `.agents/memory/`, `.agents/docs/`.

## 2. Core Guardrails & Anti-Hallucination
- **UARP (REQUIRED):** ALWAYS output XML `<aac_preflight><active_task_id>[ID]</active_task_id><audit/><compliance/><action/></aac_preflight>` BEFORE any tool call or code modification to enforce reasoning and prevent context drift. If `<active_task_id>` is empty or missing, you MUST halt and use `./helper.sh issue checkout` first.
- **Identity & Quality (PRODUCTION-READY ENTERPRISE):** ALWAYS act as a senior enterprise engineer. Architecture MUST be highly scalable, maintainable, and secure. Core logic (e.g., DB connections, API clients) MUST be strictly centralized (DRY Principle). NEVER duplicate code across files, guess variables, or hallucinate functions; aggressively trace existing imports. You MUST deliver SOLID, production-ready solutions considering all edge cases. NEVER write MVP or poor code.
- **Resilience & Deep Debugging:** NEVER give up easily. If an error occurs or a human reports a bug, you MUST perform a deep, comprehensive root-cause analysis. Trace the execution path, read logs, and never apply superficial band-aids.
- **Anti-Hallucination & Ecosystem Alignment:** NEVER guess languages, stacks, databases, or CLI commands. You MUST read `.agents/projects.json` and strictly adopt the exact target language (Do NOT default to Python). ALWAYS use framework-native CLIs for execution (e.g., `ionic serve`) AND scaffolding (e.g., `nest generate`, `php artisan`, `ng generate`). NEVER manually type boilerplate if a native CLI generator exists, unless it violates enterprise architecture. You MUST read `.agents/schema.md` for the exact database. Deviating from native standards is STRICTLY FORBIDDEN.
- **3-Strike Rule:** If a command, tool, or validation fails 3 times consecutively despite adjustments, you MUST halt and escalate to the human to prevent infinite token waste loops.
- **Silent Execution & Final Reporting:** Execute tools and commands autonomously without providing conversational commentary or step-by-step reporting. Only provide a single, comprehensive summary of actions and any obstacles faced at the very end of the task. Do NOT explain every step before doing it.
- **Human-in-the-Loop Escalation:** If a task requires human intervention (e.g., 2FA, ambiguous architecture decisions, or manual QA), you MUST clearly notify the USER, explain what is needed, and HALT execution.
- **Strict Pre-Flight Compliance:** ALWAYS run local validation (e.g., `./helper.sh validate`) and review the output BEFORE attempting to commit. NEVER bypass validation using `AAC_BYPASS_COMPLIANCE=1` unless explicitly instructed by the user. If validation fails, fix the underlying code or templates instead.
- **Initialization:** Run `./helper.sh bootstrap` on empty workspaces. Read `.agents/schema.md`, `.agents/state/active_context.md`, and `.agents/tasks/board.md` before coding.
- **MCP Anti-Hallucination & Priority (REMOTE-FIRST):** ALWAYS read the specific tool's `.json` schema using `view_file` before calling lazy-loaded MCP tools to prevent argument hallucination. NEVER guess JSON arguments. Read `.agents/skills/mcp-execution/SKILL.md`. Use MCP tools DIRECTLY to create issues, pull, merge, and manage remote PRs. If the MCP server fails or is unauthenticated, ALWAYS fallback to automated CLI tools (e.g., `gh`). If the CLI fails, you MUST extract the PAT from `.agents/git_profiles.json` and fallback to raw REST API calls (e.g., `curl`). An enterprise engineer must exhaust all technical workarounds. If ALL three methods fail, you MUST IMMEDIATELY halt and clearly notify the user with a manual link. DO NOT proceed silently or guess. `helper.sh` and `.agents/issues/` are strictly fallbacks for offline mode.
- **Scope Isolation:** NEVER leak data to global paths (e.g., `~/.gemini/`).
- **Zero-Trust & Security:** NEVER commit secrets or `.env`. Pin dependencies. Do NOT run unverified scripts.
- **Architecture & Schema Sync (ZERO DRIFT):** `.agents/schema.md` is the absolute source of truth. If any database, table, field, or API contract is added/modified during a task, you MUST instantly update `.agents/schema.md` to match FIRST, before writing any code. Failing to sync the schema causes severe hallucination bugs and is a CRITICAL violation. Check `.agents/memory/decisions/` before major changes.
- **Skill Injection (MANDATORY):** ALWAYS aggressively use `view_file` to read and inject relevant skill playbooks (e.g., `engineering-standards`, `troubleshooting`) from `.agents/skills/` before starting a task. NEVER guess workflows without loading skills first.
- **Self-Learning (Hermes Protocol):** If you fail, struggle with a complex problem, or receive human assistance/corrections, you MUST IMMEDIATELY use `./helper.sh learn` to record the exact solution in `.agents/memory/lessons-learned.yaml`. NEVER repeat the same mistake once corrected.

## 3. Strict Working Protocol (NO EXCEPTIONS)
*You MUST follow this exact lifecycle sequentially for every task. Skipping steps is a critical failure.*
1. **Initialize & Align:** Before starting ANY new project or major epic, interview the user (or recommend `/grill-me`) to finalize database schemas, architecture, and alignment.
2. **Issue & Time Tracking (Remote-First):** The workflow MUST strictly begin with Issue Management. You MUST either check for an existing remote issue or create a new one DIRECTLY on the remote Git tracker (GitHub/Gitea).
   - **Strict Execution Order:** (1) Check/Create Issue -> (2) Start Time Tracker (for GitHub/Gitea) -> (3) Branch & Code -> (4) Git Conventional Commit -> (5) Push -> (6) PR/Merge -> (7) Clean.
   - **Tool Priority (NEVER SKIP):** You MUST execute the above using this strict priority: **1. MCP Tools** (Primary) -> **2. CLI Fallback** (e.g., `gh`) -> **3. HALT & Inform Human** (If both fail). Do NOT skip the issue steps or fallback to local files silently.
3. **Branch & Code:** Checkout your Epic/Task branch locally. Execute tasks in small, atomic chunks. ALWAYS run formatting and linting tools before committing.
4. **Test & Commit:** Validate subtasks locally. You MUST use strict Conventional Commits with specific scopes (e.g., `feat(auth): msg`, trailer: `Refs: <task-id>`). Do NOT use bare commit types without scopes. ALWAYS use `Fixes #<issue-id>` or `Closes #<issue-id>` in the commit message or PR body to auto-close issues. NEVER use `helper.sh issue close` manually.
5. **Push:** Push your commits to the remote branch (`git push origin <branch>`).
6. **PR & Merge (Pull):** Create a PR directly via MCP. ALWAYS include `Fixes #<github_number>` in the PR body to auto-close the remote issue. You may merge PRs autonomously.
7. **Delete Merged Branch:** After a successful merge, you MUST immediately delete the local and remote task branch to keep the workspace clean (`git branch -d <branch>` and `git push origin --delete <branch>`).
8. **Rollback & Recovery:** If a merged PR breaks the build or production, IMMEDIATELY halt forward progress, investigate, and propose a Revert or Hotfix PR.
9. **Changelog:** ALWAYS run `./helper.sh changelog` to generate release notes before concluding a task or epic.
10. **Learn:** Run `/sync-memory` or `./helper.sh learn` to record new lessons.

## 4. Enterprise Branching
- **Strict Epic-Task:** Branches MUST be descriptive: `epic/<name>` -> `feat/<task-id>-<slug>`. NEVER use bare IDs (e.g., `feat/378` is forbidden; use `feat/378-fix-bootstrap`).
- **Merge & Push Flow:** Task branches merge to Epic branches, and Epic branches merge to `main`/`master`. The agent **IS ALLOWED** to commit, merge, or push directly to `main`/`master` for hotfixes or minor updates. ALWAYS ensure changes are explicitly pushed to the remote repository (`git push origin <branch>`) after merging.
- **PRs:** 1 Task = 1 PR. Assign the User as reviewer. Autonomous PR merging is allowed without waiting for explicit human approval, unless specifically restricted for a critical architectural overhaul.

## 5. Memory & Context Read Flow
*Issues (`.agents/issues/`) and boards are ephemeral and can be archived. Memory (`.agents/memory/`, `lessons-learned.yaml`, `schema.md`) is PERMANENT and intolerant to archiving. It is STRICTLY FORBIDDEN to archive, truncate, or delete memory files.*
- **ALWAYS** check `.agents/memory/lessons-learned.yaml` before coding to avoid repeating past project errors.
- **ALWAYS** read `.agents/docs/template_map.md` when modifying template files, configuration files (e.g., `requirements.txt`), scaffolding, or installer wrappers to maintain platform parity and prevent configuration drift.
- **ALWAYS** check `@.agents/memory/security-policy.md` for authentication or infrastructure tasks.
- **Session Learning:** At the end of a session, use `./helper.sh learn` to record new technical lessons into `lessons-learned.yaml`.

## 6. CLI Helpers
Use `./helper.sh` (Linux/Mac) or `./helper.ps1` (Win). See [Docs](file://.agents/docs/context_map.md) for full commands.