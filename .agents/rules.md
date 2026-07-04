# AAC V2 Project Rules

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

## 5. Synthesized Rules (Self-Learning Memory)
- **[Learning: Shell Scripting]** Maintain parity between Bash (.sh) and PowerShell (.ps1) helper scripts for consistent developer experience across platforms.
- **[Learning: Workspace Optimization]** Optimized scan_conversations_for_usage to read JSONL transcripts first and enforced a strict 5-minute age validation for both transcript and DB steps. Prevented dynamic limits overrides when limits are parsed directly from Markdown tables, saved direct used overrides, and implemented dynamic freshness check in run_status to trigger async background sync when budget is older than 2 minutes.; Fixed platform usage parser to correctly parse limits and used tokens from Markdown table column format and support bullet lists (*) and bold tags (**) in account/task breakdowns.; Optimized token logging latency by spawning the platform sync process as a detached background subprocess (using Popen with start_new_session/CREATE_NEW_PROCESS_GROUP), eliminating the 3-5 seconds user blocking wait.; Fixed rolling window token quotas parsing from platform /usage command by implementing multi-line block extraction (avoiding fragile line+1 checks), and added remaining tokens calculation/display to the token status CLI command.; Implemented automatic platform token usage sync by executing agy -p "/usage" and parsing the output (table, list, and console text formats) robustly via regex, avoiding infinite recursion via INTERNAL_SYNC environment guards, and improving active account detection via ~/.gemini/google_accounts.json.; Supported per-account token budget tracking in token.py by dynamically detecting active profile from git_profiles.json; Implemented a strict local token budget tracker and logging CLI subcommand 'token' supporting log, status, and reset, including dynamic date-based resets and branch-based task auto-detection; Use targeted context optimization to minimize prompt token footprint while preserving compliance with rules.; Always specify file read ranges to save context tokens.; Maintain a flat and modular directory structure to simplify agent context parsing and increase model prompt cache efficiency.
- **[Learning: Database Schema]** Strictly align API and database models with the project schemas to maintain interface integrity.
- **[Learning: documentation]** Fixed installer repository raw.githubusercontent.com URLs in README.md from rafaelghifari to rafaelghif
- **[Learning: installation]** Enforce Git source repository downloading for all installations, bootstrapping, and upgrades, and mock git clone in tests to preserve offline compatibility.
