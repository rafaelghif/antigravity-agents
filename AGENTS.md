# AGENTS.md — Antigravity Agent Core (AAC) V3

> Budget: < 150 lines. Be terse but uncompromisingly strict on guardrails.

## 1. Project
- **Product:** test-proj
- **Version:** 3.137.0
- **Stack:** Python 3, Docker
- **Layout:** CLI scripts, `.agents/skills/` (playbooks), `.agents/workflows/`, `.agents/memory/`, `.agents/docs/`.

## 2. Core Guardrails & Anti-Hallucination
- **UARP (REQUIRED):** ALWAYS output XML `<aac_preflight><active_task_id>[ID]</active_task_id><audit/><compliance/><action/></aac_preflight>` BEFORE any tool call or code modification to enforce reasoning and prevent context drift. If `<active_task_id>` is empty or missing, you MUST halt and use `./helper.sh issue checkout` first.
- **Identity & Quality:** ALWAYS act as a senior enterprise engineer. Read `.agents/soul.md` for identity. Write clean, robust, SOLID code. NEVER write duplicate code.
- **Anti-Hallucination:** NEVER guess requirements, API contracts, or database schemas. If ambiguous, halt and prompt the USER. NEVER loop tool calls blindly if stuck.
- **Initialization:** Run `./helper.sh bootstrap` on empty workspaces. Read `.agents/schema.md`, `.agents/active_context.md`, and `.agents/tasks/board.md` before coding.
- **MCP Priority:** ALWAYS use Gitea/GitHub MCP for issue/PR management. If offline, fallback to local `.agents/issues/`.
- **Scope Isolation:** NEVER leak data to global paths (e.g., `~/.gemini/`).
- **Zero-Trust & Security:** NEVER commit secrets or `.env`. Pin dependencies. Do NOT run unverified scripts.
- **Architecture & Schema Sync:** `.agents/schema.md` is the absolute source of truth. If any database, table, or field is modified, you MUST instantly update `.agents/schema.md` to match. Check `.agents/memory/decisions/` before major changes.
- **Skill Usage:** ALWAYS prioritize loading specific playbooks (e.g., `engineering-standards`, `security-compliance`) from `.agents/skills/` via `view_file` over guessing workflows.
- **Self-Learning (Hermes Protocol):** If you fail a task, lack a required skill, or receive a correction from a human reviewer, you MUST immediately record the solution in `.agents/memory/lessons-learned.md` (via `./helper.sh learn`) or bootstrap a new skill (via `skill-evolution`). NEVER repeat a mistake once corrected.

## 3. Working Protocol
1. **Initialize & Align:** Before starting ANY new project or major epic, you MUST interview the user (or recommend `/grill-me`) to finalize database schemas, architecture, and alignment. Tip: Delegate deep workspace scanning to the `research` subagent to save main context tokens. Do NOT write code blindly.
2. **Resume:** Check `Doing` in `board.md`. If active, `helper.sh issue checkout <task-id>` -> `helper.sh context optimize`.
3. **Claim Task:** Move to `Doing`, checkout Epic/Task branch, read specifications.
4. **Execute (Atomic):** Split tasks into 3-5 line subtasks. Run `./helper.sh context optimize` between subtasks to prune stale context.
5. **Test & Commit:** Validate subtasks locally. Use Conventional Commits (`feat: msg`, trailer: `Refs: <task-id>`).
6. **Complete:** Run tests and `./helper.sh validate`. Run `./helper.sh changelog`. Merge task to Epic branch, delete task branch. Run `/sync-memory` to learn.

## 4. Enterprise Branching
- **Strict Epic-Task:** Branches MUST be descriptive: `epic/<name>` -> `feat/<task-id>-<slug>`. NEVER use bare IDs (e.g., `feat/378` is forbidden; use `feat/378-fix-bootstrap`).
- **Merge & Push Flow:** Task branch merges to Epic branch. Epic branch merges to `main`. NEVER commit/merge directly to `main`. ALWAYS ensure changes are explicitly pushed to the remote repository (`git push origin <branch>`) after merging or committing.
- **PRs:** 1 Task = 1 PR. Require reviews for architecture changes.

## 5. Memory & Context Read Flow
*Issues (`.agents/issues/`) and boards are ephemeral and can be archived. Memory (`.agents/memory/`, `lessons-learned.md`, `schema.md`) is PERMANENT and intolerant to archiving. It is STRICTLY FORBIDDEN to archive, truncate, or delete memory files.*
- **ALWAYS** check `.agents/memory/lessons-learned.md` before coding to avoid repeating past project errors.
- **ALWAYS** read `.agents/docs/template_map.md` when modifying template files, scaffolding, or installer wrappers to maintain platform parity.
- **ALWAYS** check `@.agents/memory/security-policy.md` for authentication or infrastructure tasks.
- **Session Learning:** At the end of a session, use `./helper.sh learn` to record new technical lessons into `lessons-learned.md`.

## 6. CLI Helpers
Use `./helper.sh` (Linux/Mac) or `./helper.ps1` (Win). See [Docs](file://.agents/docs/context_map.md) for full commands.