# AGENTS.md — Antigravity Agent Core (AAC) V2

> Antigravity CLI prepends this file to **every** prompt in this repo. Keep it short, factual, durable. Anything only *sometimes* relevant belongs in `.agents/skills/`, `.agents/memory/`, or `.agents/tasks/` and gets pulled in on demand — see the context map below.

## 1. What this project is
- **Product:** Antigravity Agent Core (AAC) V2 — a highly optimized, project-agnostic operational workspace layout and developer protocol designed specifically for agentic coding, prompt caching, and context insulation.
- **Version:** 2.104.0
- **Stack:** Python 3
- **Repo layout:** Core CLI scripts, custom agent skills (`.agents/skills/`), workflows (`.agents/workflows/`), and project memory (`.agents/memory/`).

## 2. Non-negotiable rules
*(Listed first and emphasized — the model weights early, ALWAYS/NEVER-style rules more reliably than buried prose.)*

- **ALWAYS** perform an explicit **Rule & Schema Compliance Audit** in your thought block or response before executing any file modifications. List: (a) target files to edit, (b) active module locks, (c) applicable non-negotiable rules from `AGENTS.md` and `.agents/rules.md` (you MUST explicitly load and read `.agents/rules.md` to verify self-learned guidelines), and (d) verification of conformity with `.agents/schema.md`.
- **NEVER** commit secrets, `.env*` files, credentials, or `.agents/git_profiles.json` (the local identity-rotation file — generated from `.agents/git_profiles.example` by `./helper.sh bootstrap`). Use the secrets approach documented in `.agents/memory/architecture.md`. This rule governs *files in the repo*; runtime secret retrieval via environment variables is expected and does not conflict with the "no global config" rule below.
- **NEVER** read, edit, stage, or commit files or directories that are ignored by `.gitignore` or `.antigravityignore` (such as dependencies, build assets, logs, media, or local credentials).
- **ALWAYS** run the project's test command before marking a task `Completed`.
- **ALWAYS** check `.agents/tasks/board.md` before starting work, and update it when status changes.
- **ALWAYS** perform a Pre-Implementation Impact Analysis comparing at least two options (following the `coding-standards` playbook) to evaluate long-term maintenance, DRY principles, and simplicity *before* writing any code.
- **NEVER** write or maintain duplicate code or inline file templates (such as `cat << 'EOF'` strings of repository files) inside bootstrap, install, or helper scripts. Always rely on a single source of truth (copying locally or fetching from the repository).
- **ALWAYS** design with foresight, prioritizing public-release readiness, modularity, and future maintainability to prevent technical debt.
- **NEVER** create a new architectural decision without checking `.agents/memory/decisions/` first — supersede an old one, don't duplicate it.
- **ALWAYS** use Conventional Commits (`feat:`, `fix:`, `chore:`, `refactor:`, `docs:`, `test:`) with a `Refs: <task-id>` trailer line in the commit body — this exact, fixed format is what `./helper.sh changelog`'s parser depends on; freeform mentions of the task ID will not parse reliably.
- **NEVER** run or write raw CLI scripts directly in the workspace root; keep them organized in target directories.
- **ALWAYS** register any new custom skills in their respective subdirectory with a `SKILL.md`.
- **ALWAYS** acquire locks on modules before beginning edits to avoid conflicting parallel modifications. If a module is already locked by someone/something else, wait or escalate to the USER — never force-override or bypass an existing lock.
- **ALWAYS** run `.agents/scripts/validate.py` locally and verify it passes before proposing commits or pull requests.
- **ALWAYS** align your git branch name with an active issue ID and verify a matching issue file exists under `.agents/issues/` (e.g. branch `feat/issue-12` aligns with `.agents/issues/issue_12.md`).
- **NEVER** edit files, stage changes, or commit directly on the `main` or `master` branch.
- **ALWAYS** strictly conform to the schemas defined in `.agents/schema.md` when modifying database models or API contracts.
- **NEVER** write to or rely on global configurations, specifications, plans, designs, or artifacts outside the project directory (such as user home directory, or global agent appData/brain directories). Everything must be stored strictly within the workspace level under `.agents/` (e.g., `.agents/issues/`, `.agents/plans/`) and tracked in git to ensure multi-developer environment consistency.
- **ALWAYS** keep `CHANGELOG.md` current via `./helper.sh changelog` as part of the release step in Working Protocol §5 (Step 10) — don't run it ad hoc outside that step.
- **NEVER** loop or repeat tool calls, command executions, file checks, or code search patterns more than 3 times without making progress. If stuck, consult the `debugging` skill; if still unresolved, halt and prompt the USER for manual intervention.
- **NEVER** generate, execute, or inject malicious, obfuscated, or backdoored code. All deployed code must be human-readable, safe, secure, and follow standard secure programming guidelines.
- **NEVER** download or pull unverified remote scripts or binaries during installation or operations. All components must be sourced from secure, pinned version tags or git-tracked source repositories.
- **NEVER** expose, store, or log sensitive tokens, credentials, or private keys. Always use secure environment variable retrieval.

## 3. CLI Helper Commands Reference
All operations must be performed using `./helper.sh` (Linux/macOS) or `./helper.ps1` (Windows):
- `./helper.sh bootstrap`: Scaffolds dirs, stack detect, AGENTS.md, profile wizard.
- `./helper.sh validate`: Runs 10 audits (critical files, secrets, links, branch, sync, task board, lint, tests, locks, commits).
- `./helper.sh issue <create|list|checkout|close|sync>`: Subtask and issue lifecycle tracking.
- `./helper.sh lock <module-name>`: Acquires local locks. Unlock with `--release <module-name>`.
- `./helper.sh profile <add|switch|list|apply>`: Credentials rotation and auto-sync config.
- `./helper.sh changelog`: Conventional commits parser and SemVer version bump.
- `./helper.sh sync`: Updates skills and ADR registries.
- `./helper.sh learn "<lesson>" [--category <name>]`: Appends a lesson to `.agents/memory/lessons-learned.md` after resolving a bug or workflow issue.

## 4. Context map — what loads when

| Path | Contents | When it loads |
|---|---|---|
| `AGENTS.md` (this file) | Identity, non-negotiables, map | Always — every prompt |
| `.agents/rules.md` | Project-specific stack, style, and testing rules (language, lint, frameworks) | Always — loaded alongside `AGENTS.md` every prompt, since the §2 Compliance Audit must check it on every edit |
| `.agents/skills/adr/SKILL.md` | Standardized playbook and template for generating new Architectural Decision Records. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/ci-cd/SKILL.md` | Playbook for setting up CI/CD pipelines, automating linting, testing, building, caching, and staging release gates. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/code-review/SKILL.md` | Guidelines and checklists for performing high-quality, zero-regression code reviews. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/coding-standards/SKILL.md` | Principles, workflows, and standards for writing clean, secure, and highly optimized code, including guidelines for code writing, code review, and architectural integrity. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/contract-synchronization/SKILL.md` | Playbook for managing API contract schemas, generating client code, and verifying backend/frontend synchronization. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/conversational-agent/SKILL.md` | Playbook for translating natural language requests about tasks, profiles, locking, and validation into CLI helper executions. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/database-evolution/SKILL.md` | Playbook for writing safe database migrations, managing schema evolutions, executing reversible rollbacks, and avoiding table lock contention in enterprise environments. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/debugging/SKILL.md` | Diagnostic playbook for troubleshooting CLI errors, shell script crashes, and test failures. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/observability/SKILL.md` | Guidelines for implementing structured logging, distributed tracing (OpenTelemetry), performance metrics, and centralized error telemetry. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/performance-optimization/SKILL.md` | Guidelines for CPU profiling, identifying database query bottlenecks (N+1 queries), diagnosing memory leaks, and optimizing resource execution speeds. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/release-management/SKILL.md` | Guidelines for containerization (Dockerfile best practices), release versioning, blue-green deployment, feature flag rollouts, and post-deployment smoke verification. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/security-audit/SKILL.md` | Diagnostic playbook for scanning vulnerabilities, verifying secret exclusion, and executing OWASP Top 10 compliance audits. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/self-healing/SKILL.md` | Diagnostic and recovery playbook for resolving local git states, locked configuration files, broken workspace setups, and process deadlocks. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/task-management/SKILL.md` | Playbook for capturing design alignment from /grill-me, generating issue specifications, and managing task boards. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/skills/testing/SKILL.md` | Playbook for executing unit and integration tests, mocking external services, and structuring test suites. | Name + description always indexed; full body loads only when the task matches. Don't re-paste skill content here. |
| `.agents/workflows/*.md` | Slash-command macros (e.g. `/sync-memory`) | Only when the command is run |
| `.agents/memory/architecture.md` | Compressed system summary | Pulled on demand (`@.agents/memory/architecture.md`) before architecture-affecting work |
| `.agents/memory/decisions/` | ADRs — full reasoning | On demand, referenced from architecture.md and the `adr` skill — never auto-loaded |
| `.agents/memory/glossary.md` | Domain terms | On demand when unfamiliar terms appear |
| `.agents/memory/tech-debt.md`, `lessons-learned.md` | Known shortcuts, past incidents | On demand before related work; appended after the fact |
| `.agents/tasks/board.md` | Task board | Read at the start of every task, written at every status change |

If you're about to paste a paragraph of explanation into this file, it almost certainly belongs in a skill or memory file instead, pulled in with `@path` only when needed. That's what keeps the per-prompt token cost flat as the project grows.

## 5. Working protocol
1. **Fresh Workspace Initialization:** If starting in a completely empty project directory, the agent MUST immediately execute `./helper.sh bootstrap` to interactively setup the project name, stack (Python, Node, PHP), architecture blueprint (`schema.md`), task board, and the local git-identity profile (copies `.agents/git_profiles.example` → `.agents/git_profiles.json`, which must never be staged or committed) before writing any code.
2. **Before coding:** read `.agents/tasks/board.md`, claim the task, move it to `Doing`, and create/checkout a new branch for the task (e.g., `./helper.sh issue checkout <task-id>`).
3. **Compliance Audit:** Perform a Rule & Schema Compliance Audit (listing target files, locks, rules, and schema matching) before proposing or writing code.
4. **Task Splitting:** The agent MUST split any assigned task into small, atomic subtasks (no more than 3-5 lines of code edits per step where practical) and list them under `Implementation Subtasks` in the local issue specification file (e.g. `.agents/issues/issue_xxx.md`).
5. **Context Insulation (Single subtask focus):** The agent MUST focus on exactly ONE atomic subtask at a time. After completing a subtask, the agent MUST run validation and make a git commit with a clear Conventional Commit message referencing the task ID. This keeps the prompt cache warm and prevents context pollution.
6. **Active Context Pruning:** Between subtasks, if files are added or rules are changed, the agent MUST run `./helper.sh context optimize` to prune stale context, keeping the active context token-efficient and eliminating hallucinations.
7. **Pre-Implementation:** Perform a Pre-Implementation Impact Analysis comparing at least two options (following the `coding-standards` playbook) to evaluate long-term maintenance and UI/UX simplicity.
8. **Before any architecture-affecting change:** pull `@.agents/memory/architecture.md` and check `.agents/memory/decisions/` for a relevant ADR.
9. **While working:** prefer invoking an existing skill over re-deriving a workflow from scratch.
10. **Before marking a task `Completed`:** run all tests and `./helper.sh validate` to verify compliance. Once validation passes, run `./helper.sh changelog` to update release history, switch back to the base branch (`main` or `master`), merge the feature branch cleanly, and delete the feature branch local/remote if required.
11. **End of session:** run `/sync-memory` to fold session learnings into memory and prune anything stale (see `.agents/workflows/sync-memory.md`).

## 6. Git & review
- Branches: `feat/<task-id>-slug`, `fix/<task-id>-slug`.
- All code edits must be done on the designated branch. Committing to base branches (`main` or `master`) directly is strictly prohibited.
- One task = one PR where practical; link the task ID in the PR description.
- No self-merging architecturally significant PRs — a second reviewer (human or the `code-review` skill) signs off first.
- When a task is finished, checkout the base branch, merge the feature branch, and delete the feature branch.

## 7. Tool permissions
Default to `request-review` in `./helper.sh config` for this repo (pauses before destructive/file-write actions). Reserve `proceed-in-sandbox` for disposable environments only. Never set `always-proceed` on a repo with reachable production credentials.

## 8. Maintaining this file
Reviewed like code. Budget: stay under ~150 lines. If it grows past that, move the newest, least-universal addition into a skill or memory file and leave a one-line pointer here instead.