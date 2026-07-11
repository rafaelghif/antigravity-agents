# AAC V3 Project Rules

These rules extend the core guidelines in `AGENTS.md` with project-specific language and tool specifications.

> **Scope note:** Section 1–3 below govern **AAC's own source code** (the CLI tool itself, which is built in Python). They do **not** apply to whatever stack a *managed/target* project uses — that's handled by the stack-agnostic detection described in Section 4.

## 1. Programming Language & Tools (AAC's own codebase)
- Use **Docker** for the main product stack.
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

## 4. Enterprise-Grade Standards
- **Clean Code & Patterns:** Follow SOLID design principles, write highly modular code, and use standard architectural design patterns (like Clean Architecture or Layered/MVC where appropriate).
- **Scalability:** Design APIs and systems to handle concurrency, avoid locking contentions, optimize memory and thread pool sizes, and avoid N+1 query patterns.
- **Security:** Avoid OWASP Top 10 vulnerabilities (SQL Injection, XSS, CSRF, insecure command execution). Always sanitize inputs. Keep secrets strictly in environment variables.
- **Performance:** Cache hot paths, optimize database queries with indexing, use non-blocking operations where appropriate, and keep CPU/memory footprint low.
- **Maintainability:** Document everything clearly with type hints/docstrings, write robust error handling (avoid bare print statements, use structured logging), and maintain strict DRY compliance.
- **Workspace Isolation & Schema Integrity:** Keep all configurations, database schemas, tables, and relationship designs strictly within the workspace level under `.agents/schema.md` or split into modular files under `.agents/schemas/*.md` (e.g. `users.md`, `billing.md`). Never write, expose, or leak workspace data/artifacts to global paths (such as `~/.gemini/` or home folder configs). If database structures are changed or discussed, the agent MUST immediately update the database schema documentation (both `.agents/schema.md` and the matching modular file under `.agents/schemas/`) to keep them synchronized. Document all foreign keys and associations under `## Cross-Module References` using relative markdown links to referenced schema files. The agent must load only the specific schema modules relevant to the active subtasks on-demand to optimize context sizes. When designing, evaluate and document 10-year foresight considerations (scalability up to 10-100x volume, cascading deletions, partition strategies, failover resilience).
- **Holistic Thinking Profiles:** Systematically apply Engineering Thinking (SOLID decoupling, TDD, strict typing, cognitive complexity control), Management Thinking (atomic task checklists, module locking, progress visibility), and Production/Ops Thinking (structured logging, containerization, backward-compatibility, and sandboxed execution boundaries) to guarantee enterprise-grade outputs. Always execute a mental **Self-Refinement & Pre-flight Protocol** (verify schema sync, active locks, 10-year foresight scale, and workspace boundaries) before any tool invocation that writes or edits files to eliminate context drift and hallucinations.

## 5. Plug-and-Play Adaptation & Self-Learning
- **Stack Adaptiveness**: The agent layout is project-agnostic. `./helper.sh bootstrap` (a thin wrapper around `bootstrap.py` — all detection logic lives in the Python script, not duplicated in the shell wrapper, per the no-duplicate-templates rule in `AGENTS.md`) auto-detects and supports any programming language stack (e.g. Python, Node, PHP, Go, Rust, Java, C#) for the *target* project, without strict folder structure constraints.
- **Continuous Self-Learning**: After resolving any bug, workflow issue, or optimization, the agent MUST run `./helper.sh learn "<lesson>"` (optionally with `--category <name>`) to append the lesson in `.agents/memory/lessons-learned.md`. Always review this file at the start of work. (Also listed in `AGENTS.md` §3 CLI reference.)
- **Token & Context Efficiency**: The agent MUST record found filepaths in its thinking block and is prohibited from calling search tools (`grep_search`, `list_dir`) for the same files or directories more than once per conversation session. The agent MUST use the narrowest possible line range when using the `view_file` tool to read files.
- **Prompt Caching**: To preserve prompt cache state and save context tokens, reuse retrieved file content and search results from previous turns instead of making repetitive tool calls.
- **Template & Wrapper Parity**: Before modifying templates, wrappers (bootstrap, install, helper), or generated configs, the agent MUST read `.agents/docs/template_map.md` to ensure exact parity across Linux (Bash) and Windows (PowerShell) platforms, preventing platform-drift and token waste.

## 6. Synthesized Rules (Self-Learning Memory)
- **[Learning: configuration]** Integrated GitHub API MCP server configuration inside mcp_config.json and appended .agents/git_profiles.json rotation and monorepo project configurations mapping to template_map.md.; Documented config template-to-target file relationships and Linux/Windows CLI wrapper parity to prevent drift, resolved rules sync duplication bugs, and secured mcp_server path registry.
- **[Learning: reconnaissance]** Decoupled modular stack detectors in recon.py to dynamically adapt test/build commands and frameworks (e.g., C# WinForms/WPF/Web, PHP Pest/PHPUnit, Ruby RSpec) across all major programming ecosystems.
- **[Learning: Shell Scripting]** Maintain parity between Bash (.sh) and PowerShell (.ps1) helper scripts for consistent developer experience across platforms.
- **[Learning: Workspace Optimization]** Optimized scan_conversations_for_usage to read JSONL transcripts first and enforced a strict 5-minute age validation for both transcript and DB steps. Prevented dynamic limits overrides when limits are parsed directly from Markdown tables, saved direct used overrides, and implemented dynamic freshness check in run_status to trigger async background sync when budget is older than 2 minutes.; Fixed platform usage parser to correctly parse limits and used tokens from Markdown table column format and support bullet lists (*) and bold tags (**) in account/task breakdowns.
- **[Learning: Database Schema]** Strictly align API and database models with the project schemas to maintain interface integrity.
