# AGENTS.md — Antigravity Agent Core (AAC) V3

> Antigravity CLI prepends this file to **every** prompt in this repo. Keep it short, factual, durable. Anything only *sometimes* relevant belongs in `.agents/skills/`, `.agents/memory/`, or `.agents/tasks/` and gets pulled in on demand — see the context map below.

## 1. What this project is
- **Product:** test-proj
- **Version:** 3.84.0
- **Stack:** Docker
- **Repo layout:** Core CLI scripts, custom agent skills (`.agents/skills/`), workflows (`.agents/workflows/`), and project memory (`.agents/memory/`).

## 2. Non-negotiable rules
*(Listed first and emphasized — the model weights early, ALWAYS/NEVER-style rules more reliably than buried prose.)*

- **ALWAYS** perform an explicit **Rule & Schema Compliance Audit** in your thought block or response before executing any file modifications. List: (a) target files to edit, (b) active module locks, (c) applicable non-negotiable rules from `AGENTS.md` and `.agents/rules.md` (you MUST explicitly load and read `.agents/rules.md` to verify self-learned guidelines), and (d) verification of conformity with `.agents/schema.md`. Run a mental **Self-Refinement & Pre-flight Protocol** before executing tool calls. Ask yourself: (1) Does this change align with `.agents/schema.md`? (2) Am I editing a locked module? (3) Have I evaluated 10-year scale? (4) Does this write leak configs globally? You MUST write out this brief pre-flight check to ground your parameters and eliminate context drift/hallucinations.
- **ALWAYS** load, read, and strictly adhere to the agent core persona, tone guidelines, and philosophies defined in the agent soul profile [.agents/soul.md](file://.agents/soul.md) in every response and action to guarantee consistent enterprise-grade engineering identity across all platforms and accounts.
- **ALWAYS** load and read the workspace's `.agents/active_context.md`, `.agents/schema.md`, the active issue specification file `.agents/issues/issue_[id].md`, and any custom workspace-level memory files (such as `memory.md`, `brain.md`, or custom context files in the root or `.agents/` directory) at the very beginning of the first conversation turn to align on task checklist, database/API schemas, scope boundaries, and local workspace memory before formulating any implementation plan or writing code.
- **ALWAYS** distinguish between **Discussions** (informational queries, design questions, general research, diagnostics) and **Tasks** (codebase writes/modifications). Never create Git branches, task board entries, or commits for informational or diagnostic discussions. Only trigger the branch-and-issue tracking workflow when actual file edits/creations are required.
- **NEVER** commit secrets, `.env*` files, credentials, or `.agents/git_profiles.json` (the local identity-rotation file — generated from `.agents/git_profiles.example` by `./helper.sh bootstrap`). Use the secrets approach documented in `.agents/memory/architecture.md`. This rule governs *files in the repo*; runtime secret retrieval via environment variables is expected and does not conflict with the "no global config" rule below.
- **NEVER** read, edit, stage, or commit files or directories that are ignored by `.gitignore` or `.antigravityignore` (such as dependencies, build assets, logs, media, or local credentials).
- **ALWAYS** run the project's test command before marking a task `Completed`.
- **ALWAYS** check `.agents/tasks/board.md` before starting work, and update it when status changes.
- **ALWAYS** perform a Pre-Implementation Impact Analysis comparing at least two options (following the `coding-standards` playbook) to evaluate long-term maintenance, DRY principles, and simplicity *before* writing any code.
- **NEVER** write or maintain duplicate code or inline file templates (such as `cat << 'EOF'` strings of repository files) inside bootstrap, install, or helper scripts. Always rely on a single source of truth (copying locally or fetching from the repository).
- **ALWAYS** design with foresight, prioritizing public-release readiness, modularity, and future maintainability to prevent technical debt.
- **NEVER** create a new architectural decision without checking `.agents/memory/decisions/` first — supersede an old one, don't duplicate it.
- **ALWAYS** use Conventional Commits (`feat:`, `fix:`, `chore:`, `refactor:`, `docs:`, `test:`) with a `Refs: <task-id>` trailer line in the commit body. The subject line MUST be descriptive of the technical changes made; **NEVER** use generic placeholder subjects (e.g. `fix: issue-122` or `chore: task-100`) without explanation. This exact format is what `./helper.sh changelog`'s parser depends on.
- **NEVER** run or write raw CLI scripts directly in the workspace root; keep them organized in target directories.
- **ALWAYS** register any new custom skills in their respective subdirectory with a `SKILL.md`.
- **ALWAYS** acquire locks on modules before beginning edits to avoid conflicting parallel modifications. If a module is already locked by someone/something else, wait or escalate to the USER — never force-override or bypass an existing lock.
- **ALWAYS** run `.agents/scripts/validate.py` locally and verify it passes before proposing commits or pull requests.
- **ALWAYS** align your git branch name with an active issue ID and verify a matching issue file exists under `.agents/issues/` (e.g. branch `feat/issue-12` aligns with `.agents/issues/issue_12.md`).
- **NEVER** edit files, stage changes, or commit directly on the `main` or `master` branch.
- **ALWAYS** strictly conform to and document all database models, tables, relationships, or API contracts in `.agents/schema.md`. If data layout grows large, split schemas into modular files under `.agents/schemas/*.md` (e.g. `users.md`, `billing.md`) with `.agents/schema.md` acting as the master directory. If any data structures, tables, databases, or schemas are discussed, proposed, or modified, the agent MUST immediately update `.agents/schema.md` (and any matching modular schema file under `.agents/schemas/`) to reflect these changes before proceeding, ensuring subsequent sessions understand the data flow without reading past transcripts. To optimize token budget, the agent MUST load only the specific schema modules relevant to the active subtasks checklist on-demand. Cross-module table relationships MUST be explicitly documented under a `## Cross-Module References` header in each module file using descriptive markdown file links to target schema files; the agent must proactively load referenced dependencies when modifying or analyzing related structures.
- **ALWAYS** track and log token budget consumption at the end of each subtask or user response by running `./helper.sh token log <prompt_tokens> <completion_tokens> [--task <task-id>]` to prevent daily/monthly budget overruns and guarantee strict token auditing.
- **NEVER** write, expose, or leak project-specific configurations, specifications, plans, designs, database data, or artifacts to the global system level (such as user home directory, global agent appData/brain directories, or global databases). The agent must operate strictly at the workspace level, keeping all inputs, outputs, and intermediate states completely isolated within the repository directory to ensure multi-developer alignment and prevent global environment leakage.
- **ALWAYS** keep `CHANGELOG.md` current via `./helper.sh changelog` as part of the release step in Working Protocol §5 (Step 10) — don't run it ad hoc outside that step.
- **NEVER** loop or repeat tool calls, command executions, file checks, or code search patterns more than 3 times without making progress. If stuck, consult the `debugging` skill; if still unresolved, halt and prompt the USER for manual intervention.
- **ALWAYS** check available skill descriptions in the prompt or `context_map.md` before starting a task. You MUST load the corresponding skill's playbook file (via `view_file` on `.agents/skills/<name>/SKILL.md`) **ONLY** if the current task directly matches the skill's purpose (e.g. `debugging` for failures, `ci-cd` for pipelines, `security-audit` for security/credentials edits, `testing` for writing tests). Do NOT load skills speculatively or keep them in memory if they are not active.
- **NEVER** retrieve the same files or run the same codebase searches (`grep_search`, `list_dir`) more than once per task. Cache the results in your thinking block to maximize prompt caching effectiveness and minimize token usage.
- **NEVER** generate, execute, or inject malicious, obfuscated, or backdoored code. All deployed code must be human-readable, safe, secure, and follow standard secure programming guidelines.
- **NEVER** download or pull unverified remote scripts or binaries during installation or operations. All components must be sourced from secure, pinned version tags or git-tracked source repositories.
- **NEVER** expose, store, or log sensitive tokens, credentials, or private keys. Always use secure environment variable retrieval.
- **ALWAYS** specify pinned dependency versions (never use wildcard `*` or blank versions) to ensure deterministic, reproducible builds and block supply chain attacks.
- **ALWAYS** implement robust, explicit error handling with structured logging or standardized traceback reporting instead of bare prints or silent exception catches.
- **NEVER** bypass static code checks, compilation guards, or unit testing gates on base branches; all production changes must pass local validations before pull request submission.
- **ALWAYS** explicitly ask the user for specifications, database requirements, environment configurations, frameworks/libraries, and detailed features **BEFORE** starting development or writing any code for a new project, feature, or web application. You **MUST NEVER** assume, speculate, or hallucinate these requirements. If they are not fully detailed, you **MUST** prompt the user to provide them or suggest using the `/grill-me` slash command to align on design decisions first.
- **ALWAYS** act as a self-driving, proactive agent. Do not halt or wait for user instructions between atomic subtasks on your checklist. Instead, loop your thoughts, chain tool calls, and execute the next subtasks sequentially in a single turn (or across consecutive turns without prompting the user for intermediate feedback) until the entire issue is fully completed. If there is any doubt or ambiguity in specifications, the agent **MUST** halt and prompt the USER for clarification rather than speculating or hallucinating.
- **NEVER** run destructive Git commands such as `git reset --hard`, `git clean -fd`, `git checkout -- .`, `git checkout .`, or `git push --force`. If you need to revert changes, discard files, or clean untracked assets, you MUST do it selectively or ask the programmer first.
- **ALWAYS** write enterprise-grade code that is clean, secure, performant, scalable, and highly maintainable:
  - *Security:* Perform strict input validation and sanitization. Use parameterized queries or ORMs. NEVER hardcode secrets or credentials. Prevent OWASP Top 10 vulnerabilities.
  - *Performance & Scale:* Avoid blocking I/O on primary threads, design for thread-safety, avoid N+1 database queries, and optimize memory/resource usage.
  - *Maintainability:* Structure code modularly (SOLID principles, Clean Architecture), write comprehensive error handling (with tracebacks/structured logging), and document public APIs with type annotations and docstrings.
  - *10-Year Foresight:* Evaluate long-term maintainability, API forward-compatibility, partition growth (10-100x volume), cascading delete risks, soft delete strategies, lock contention, and failover resilience before committing database or core engine designs.
  - *Engineering Thinking:* Follow structured problem-solving, TDD, strict type constraints, PEP 8/SOLID standards, and keep cognitive complexity low (short functions, guard clauses).
  - *Management Thinking:* Align with the task board, split work into documented atomic subtasks, track budget limits, manage module locks, and maintain complete progress visibility.
  - *Production/Ops Thinking:* Ensure robust observability (structured JSON logs, telemetry, health endpoints), deployment containerization, backward-compatibility, and failover/concurrency safety.
- **ALWAYS** check `.agents/memory/lessons-learned.md` before coding to avoid repeating past errors, and run `./helper.sh learn` to record new technical lessons at the end of the task to foster continuous self-learning.
- **ALWAYS** perform a Pre-Implementation Impact Analysis mapping all files and command dependencies affected by a change. When modifying CLI commands, options, or core settings, the agent MUST explicitly review and synchronize the installer files (`install.sh`/`install.ps1`) and bootstrap wrappers (`bootstrap.sh`/`bootstrap.ps1`) to prevent platform-drift or missing options.
- **ALWAYS** translate and expand brief or informal user instructions (e.g. "A" or "continue previous task") into a comprehensive, enterprise-grade structured implementation plan inside the active issue specification file. The agent MUST perform systematic prompt expansion, defining clear checklist tasks, acceptance criteria, and compliance audits. The agent MUST strictly rely on and respect the user's human-in-the-loop command approval gates (never attempting to bypass or automate approval for proposed commands) and proactively verify ambiguous details interactively using `/grill-me` or interactive questions to prevent hallucinated actions.

## 3. CLI Helper Commands Reference

All workspace operations must be performed using `./helper.sh` (Linux/macOS) or `./helper.ps1` (Windows). For the complete command list, flags, and options, see the [CLI Commands Reference](file://.agents/docs/context_map.md#1-cli-helper-commands-reference).

## 4. Context map — what loads when

For the complete description of workspace metadata, ADRs, playbooks, memory structures, and their loading behaviors, see the [Workspace Context Map](file://.agents/docs/context_map.md#2-context-map--what-loads-when).


## 5. Working protocol
1. **Fresh Workspace Initialization:** If starting in a completely empty project directory, the agent MUST immediately execute `./helper.sh bootstrap` to interactively setup the project name, stack (Python, Node, PHP), architecture blueprint (`schema.md`), task board, and the local git-identity profile (copies `.agents/git_profiles.example` → `.agents/git_profiles.json`, which must never be staged or committed) before writing any code.
2. **Before coding:** read `.agents/tasks/board.md`, claim the task, move it to `Doing`, create/checkout a new branch for the task (e.g., `./helper.sh issue checkout <task-id>`), run `./helper.sh context optimize`, and read `.agents/active_context.md` to align on active scope, checklist, and rules.
3. **Compliance Audit:** Perform a Rule & Schema Compliance Audit (listing target files, locks, rules, and schema matching using `.agents/active_context.md` as the primary source) before proposing or writing code.
4. **Task Splitting:** The agent MUST split any assigned task into small, atomic subtasks (no more than 3-5 lines of code edits per step where practical) and list them under `Implementation Subtasks` in the local issue specification file (e.g. `.agents/issues/issue_xxx.md`).
5. **Context Insulation (Single subtask focus):** The agent MUST focus on exactly ONE atomic subtask at a time. After completing a subtask, the agent MUST run validation and make a git commit with a clear Conventional Commit message referencing the task ID. This keeps the prompt cache warm and prevents context pollution.
6. **Active Context Pruning:** Between subtasks, if files are added or rules are changed, the agent MUST run `./helper.sh context optimize` to prune stale context, keeping the active context token-efficient and eliminating hallucinations.
7. **Pre-Implementation:** Perform a Pre-Implementation Impact Analysis comparing at least two options (following the `coding-standards` playbook) to evaluate long-term maintenance and UI/UX simplicity.
8. **Before any architecture-affecting change:** pull `@.agents/memory/architecture.md` and check `.agents/memory/decisions/` for a relevant ADR.
9. **While working:** prefer invoking an existing skill over re-deriving a workflow from scratch. When a task matches a skill's description, load that skill's `SKILL.md` using `view_file` to align on execution steps, ensuring the skill is used efficiently.
10. **Before marking a task `Completed`:** run all tests and `./helper.sh validate` to verify compliance. Once validation passes, run `./helper.sh changelog` to update release history, switch back to the base branch (`main` or `master`), merge the feature branch cleanly, and delete the feature branch local/remote if required.
11. **End of session:** run `/sync-memory` to fold session learnings into memory and prune anything stale (see `.agents/workflows/sync-memory.md`).

## 6. Git & review
- Branches: `feat/<task-id>-slug`, `fix/<task-id>-slug`.
- All code edits must be done on the designated branch. Committing to base branches (`main` or `master`) directly is strictly prohibited.
- One task = one PR where practical; link the task ID in the PR description.
- No self-merging architecturally significant PRs — a second reviewer (human or the `code-review` skill) signs off first.
- When a task is finished, checkout the base branch, merge the feature branch, and delete the feature branch.

## 7. Technical Alignment & Decision Capture Flow
When aligning on technical details, features, or database specifications:
1. **Interactive Alignment**: Use `/grill-me` (or interactive dialogue) to query stack details, library versions, features, and database schemas.
2. **Alignment Storage (Workspace Level)**:
   * **Database schemas/models/API blueprints**: Record strictly to `.agents/schema.md` or modular files under `.agents/schemas/` (if database size is large). Whenever database structures, tables, or fields are discussed, updated, or created, the agent MUST immediately record them here to preserve data layout visibility.
   * **Task details & specification checklist**: Record strictly to `.agents/issues/issue_[id].md`.
   * **Architectural patterns/ADRs**: Record strictly to `.agents/memory/decisions/` and index in `.agents/memory/architecture.md`.
   * **Session learnings**: Record to `.agents/memory/lessons-learned.md` using `./helper.sh learn`.
3. **Workspace Read Flow**: Before coding, the agent MUST read `.agents/schema.md` (for database conformity, index registry, and to discover modular schemas under `.agents/schemas/`), `.agents/active_context.md` (for the active subtasks checklist), `.agents/docs/template_map.md` (for template-to-target and installer/bootstrap platform parity mappings), and `@.agents/memory/architecture.md` (for architectural boundaries). Depending on scope, load `@.agents/memory/milestones.md` for roadmap/release alignment, `@.agents/memory/security-policy.md` for security/GPG runbooks, and `@.agents/docs/collaboration.md` for team coordination and lock resolution. To optimize context token limits, the agent MUST load only the specific schema modules under `.agents/schemas/*.md` that are relevant to the active subtasks checklist on-demand.
4. **Skill Loading Optimization**: Custom playbooks under `.agents/skills/` MUST be loaded on-demand via `view_file` only when a task matches the skill's description. They are strictly prohibited from being auto-loaded globally to optimize context size.

## 8. Tool permissions
Default to `request-review` in `./helper.sh config` for this repo (pauses before destructive/file-write actions). Reserve `proceed-in-sandbox` for disposable environments only. Never set `always-proceed` on a repo with reachable production credentials.

## 9. Maintaining this file
Reviewed like code. Budget: stay under ~150 lines. If it grows past that, move the newest, least-universal addition into a skill or memory file and leave a one-line pointer here instead.