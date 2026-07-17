# AAC V3 Project Rules

These rules extend the core guidelines in `AGENTS.md` with project-specific language and tool specifications.

> **Scope note:** Section 1–3 below govern **AAC's own source code** (the CLI tool itself, which is built in Python). They do **not** apply to whatever stack a *managed/target* project uses — that's handled by the stack-agnostic detection described in Section 4.

## 1. Programming Language & Tools (AAC's own codebase)
- Use **Python 3, Docker** for the main product stack.
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
- **Senior Developer Mindset:** Design with 10-year foresight, keep cognitive complexity low, and write robust code.
- **Code Optimization & Security:** Strict guidelines for Performance, Security, and Maintainability are offloaded to `engineering-standards` and `security-compliance` playbooks.
- **Clean Code & Patterns:** SOLID design principles and Clean/Layered/MVC patterns are highly recommended for modular enterprise projects, but can be relaxed or omitted for lightweight scripts, single-file utilities, prototypes, and custom layouts to maintain flexibility.
- **Workspace Isolation & Schema Integrity:** Keep all database schemas strictly in `.agents/schema.md` or modular files under `.agents/schemas/*.md`. Never leak artifacts to global paths (e.g. `~/.gemini/` or home directories). Immediately document any schema changes to maintain synchronization.
- **UARP & Holistic Profiles:** Apply Engineering, Management, and Ops Thinking. The XML `<aac_preflight>` block defined in `AGENTS.md` is strictly enforced. You MUST provide a valid `<active_task_id>`. If you don't have one, claim one via `helper.sh issue checkout`.
- **Token-Optimized Board Checking:** NEVER use `view_file` to read the entire `.agents/tasks/board.md` to save tokens. Instead, use `grep_search` to filter `## Doing` or `## Todo`.
- **Git Auto-Closing & Remote-First MCP:** ALWAYS use MCP tools DIRECTLY to create issues, pull, merge, and manage remote PRs. Do NOT use local `helper.sh issue close` or edit `board.md` manually unless MCP is completely unavailable. If offline, commit with `Closes #ID` to trigger local Git hooks.
- **Architectural Reference Blueprints:** Read `.agents/blueprints/` guides (e.g. `clean-architecture.md`, `monorepo.md`) to align on structural layout before planning new architectural components.
- **Human Programmer Mode:** Human developers are granted warning-only bypasses for quality and bureaucratic checks (linting, module locks, etc.).
- **Proactive Skill Loading:** You MUST proactively load the required `SKILL.md` via `view_file` at the start of tasks matching that domain (e.g., `testing`, `engineering-standards`, `security-compliance`, `troubleshooting`). Bypassing required playbook reads is strictly audited and blocks execution.

## 5. Plug-and-Play Adaptation & Self-Learning
- **Stack Adaptiveness**: The agent layout is project-agnostic. `./helper.sh bootstrap` (a thin wrapper around `bootstrap.py` — all detection logic lives in the Python script, not duplicated in the shell wrapper, per the no-duplicate-templates rule in `AGENTS.md`) auto-detects and supports any programming language stack (e.g. Python, Node, PHP, Go, Rust, Java, C#) for the *target* project, without strict folder structure constraints.
- **Continuous Self-Learning**: After resolving any bug, workflow issue, or optimization, the agent MUST run `./helper.sh learn "<lesson>"` (optionally with `--category <name>`) to append the lesson in `.agents/memory/lessons-learned.md`. Always review this file at the start of work. (Also listed in `AGENTS.md` §3 CLI reference.)
- **Token & Context Efficiency**: The agent SHOULD record found filepaths in its thinking block to minimize token footprint. Repeated calling of search tools (`grep_search`, `list_dir`) or file retrieval for the same paths is allowed when required to perform a deeper analysis, verify workspace state, or confirm modifications.
- **Prompt Caching**: To preserve prompt cache state and save context tokens, reuse retrieved file content and search results from previous turns where possible, but feel free to re-query files or paths to ensure analytical depth and verification correctness.
- **Template & Wrapper Parity**: Before modifying templates, wrappers (bootstrap, install, helper), or generated configs, the agent MUST read `.agents/docs/template_map.md` to ensure exact parity across Linux (Bash) and Windows (PowerShell) platforms, preventing platform-drift and token waste.

## 6. Synthesized Rules (Self-Learning Memory)
- **[Learning: Git & Security]** Validate GPG key imports and developer identity rotation rules locally to safeguard credentials.
- **[Learning: OS Compatibility / PowerShell]** Use cross-platform path resolution helpers instead of hardcoded OS separators to prevent Windows/Linux path mismatches.
