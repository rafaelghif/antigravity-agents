# AAC V3 Project Rules

These rules extend the core guidelines in `AGENTS.md` with project-specific language and tool specifications.

> **Scope note:** Section 1–3 below govern **AAC's own source code** (the CLI tool itself, which is built in Python). They do **not** apply to whatever stack a *managed/target* project uses — that's handled by the stack-agnostic detection described in Section 4.

## 1. Programming Language & Tools (AAC's own codebase)
- Use **Python** for the main product stack.
- Rely on the standard library where possible to minimize external dependencies.
- Use **Bash** for lightweight POSIX-compatible wrapper scripts. Ensure path-separators and directory check logic are safe for multi-platform execution (e.g. using `python3` wrappers on Windows).

## 2. Style Guidelines & Linting
- Follow **PEP 8** style guidelines for all Python code.
- Always include clear docstrings for public classes, modules, and functions.
- Keep functions short, focused, and under 50 lines where practical.
- Commit message subjects must be descriptive and explain the technical change made; generic messages such as `fix: issue-122` or `chore: task-100` are strictly forbidden. Always explain what was changed (e.g. `fix(perf): cap thread pool size`).

## 3. Testing Requirements
- Every new feature or command module MUST have corresponding unit tests under `tests/`.
- Tests must use standard `unittest` or `pytest` frameworks.
- Mock all filesystem or external command calls to ensure tests remain deterministic and fast.

## 4. Plug-and-Play Adaptation & Self-Learning
- **Stack Adaptiveness**: The agent layout is project-agnostic. `./helper.sh bootstrap` (a thin wrapper around `bootstrap.py` — all detection logic lives in the Python script, not duplicated in the shell wrapper, per the no-duplicate-templates rule in `AGENTS.md`) auto-detects and supports any programming language stack (e.g. Python, Node, PHP, Go, Rust, Java, C#) for the *target* project, without strict folder structure constraints.
- **Continuous Self-Learning**: After resolving any bug, workflow issue, or optimization, the agent MUST run `./helper.sh learn "<lesson>"` (optionally with `--category <name>`) to append the lesson in `.agents/memory/lessons-learned.md`. Always review this file at the start of work. (Also listed in `AGENTS.md` §3 CLI reference.)
- **Token & Context Efficiency**: The agent MUST record found filepaths in its thinking block and is prohibited from calling search tools (`grep_search`, `list_dir`) for the same files or directories more than once per conversation session. The agent MUST use the narrowest possible line range when using the `view_file` tool to read files.
- **Strict Token Budget Tracking**: The agent MUST log all token usage at the end of each user response or subtask by executing `./helper.sh token log <prompt> <completion> [--task <id>].`
- **Strict Task Splitting & Context Insulation**: Before starting any task, the agent MUST split the work into small, atomic subtasks in the issue specification. The agent MUST work on only one subtask at a time, running validation and committing after each atomic step, and running `./helper.sh context optimize` to prune stale history and avoid hallucination.
- **ALWAYS** explicitly ask the user for specifications, database requirements, environment configurations, frameworks/libraries, and detailed features **BEFORE** starting development or writing any code for a new project, feature, or web application. You **MUST NEVER** assume, speculate, or hallucinate these requirements. If they are not fully detailed, you **MUST** prompt the user to provide them or suggest using the `/grill-me` slash command to align on design decisions first.
- **ALWAYS** act as a self-driving, proactive agent. Do not halt or wait for user instructions between atomic subtasks on your checklist. Instead, loop your thoughts, chain tool calls, and execute the next subtasks sequentially in a single turn (or across consecutive turns without prompting the user for intermediate feedback) until the entire issue is fully completed. If there is any doubt or ambiguity in specifications, the agent **MUST** halt and prompt the USER for clarification rather than speculating or hallucinating.
- **ALWAYS** chain consecutive commands or prompt loops internally (e.g. running syntax compilation, unit tests, and validation checks sequentially) to minimize user interactions, achieving zero-touch verification whenever performing changes.
- **ALWAYS** perform a Pre-Implementation Impact Analysis mapping all files and command dependencies affected by a change. When modifying CLI commands, options, or core settings, the agent MUST explicitly review and synchronize the installer files (`install.sh`/`install.ps1`) and bootstrap wrappers (`bootstrap.sh`/`bootstrap.ps1`) to prevent platform-drift or missing options.
- **Workspace-Level Artifacts Constraint**: To ensure Git tracking and multi-developer consistency, the agent MUST write all plans, designs, specifications, impact analyses, and markdown artifacts strictly under the project's `.agents/` directory (e.g. `.agents/plans/` and `.agents/issues/`) or project-level files (such as `memory.md`, `brain.md`). The agent is strictly prohibited from writing these files to global agent appData/brain directories or user home directories, overriding any standard artifact path instructions. All files under `.agents/` must be tracked in Git to prevent global data leakage.
- **Technical Alignment & Decision Capture Flow**: When aligning on specifications (e.g. via `/grill-me`), record database models to `.agents/schema.md`, task checklists to `.agents/issues/issue_[id].md`, and architectural ADRs to `.agents/memory/decisions/`. Read these localized paths before writing any code. Load playbooks under `.agents/skills/` on demand via `view_file` only when a task matches the skill's description (O(1) matching constraint) to optimize context tokens.
- **Strict Early Workspace Reads**: The agent MUST load and read the workspace's `.agents/active_context.md`, `.agents/schema.md`, the active issue specification file `.agents/issues/issue_[id].md`, and any custom workspace-level memory files (such as `memory.md`, `brain.md`, or custom context files in the root or `.agents/` directory) at the very beginning of the first conversation turn to align on task checklist, database/API schemas, scope boundaries, and local workspace memory before formulating any implementation plan or writing code.
- **Prompt Caching & Token Optimization**: To preserve the Gemini prompt cache state and save context tokens, the agent MUST reuse retrieved file content and search results from previous turns instead of making repetitive tool calls (like reading the same file range twice or re-running identical grep queries). Keep the active context size small and clean by only reading target files.

## 5. Synthesized Rules (Self-Learning Memory)
- **[Learning: Shell Scripting]** Maintain parity between Bash (.sh) and PowerShell (.ps1) helper scripts for consistent developer experience across platforms.
- **[Learning: Workspace Optimization]** Optimized scan_conversations_for_usage to read JSONL transcripts first and enforced a strict 5-minute age validation for both transcript and DB steps. Prevented dynamic limits overrides when limits are parsed directly from Markdown tables, saved direct used overrides, and implemented dynamic freshness check in run_status to trigger async background sync when budget is older than 2 minutes.; Fixed platform usage parser to correctly parse limits and used tokens from Markdown table column format and support bullet lists (*) and bold tags (**) in account/task breakdowns.
- **[Learning: Database Schema]** Strictly align API and database models with the project schemas to maintain interface integrity.
- **[Learning: documentation]** Fixed installer repository raw.githubusercontent.com URLs in README.md from rafaelghifari to rafaelghif
- **[Learning: installation]** Enforce Git source repository downloading for all installations, bootstrapping, and upgrades, and mock git clone in tests to preserve offline compatibility.
