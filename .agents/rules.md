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
- Commit message subjects must be descriptive, explain the technical change, and MUST include a specific scope; generic messages or bare commits such as `fix: issue-122` or `chore: task-100` are strictly forbidden. Always use a scope to explain what component was changed (e.g. `fix(core): cap thread pool size`, `feat(auth): add login`).

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
- **Strict Pre-Flight Audits:** ALWAYS run `./helper.sh validate` locally and verify its output before attempting to run `git commit`. You MUST NEVER bypass validation using `AAC_BYPASS_COMPLIANCE=1` unless the user explicitly orders it. If validation fails, fix the code and templates.
- **Token-Optimized Board Checking:** NEVER use `view_file` to read the entire `.agents/tasks/board.md` to save tokens. Instead, use `grep_search` to filter `## Doing` or `## Todo`.
- **Git Auto-Closing & Remote-First MCP:** ALWAYS use MCP tools DIRECTLY to create issues, pull, merge, and manage remote PRs on GitHub/Gitea. This is STRICTLY MANDATORY unless the Git MCP server is explicitly marked as `"disabled": true` in `.agents/mcp_config.json`. DO NOT create offline `.agents/issues/` markdown files unless explicitly in offline mode. For PR creation or commits, you MUST include `Fixes #<github_number>` or `Closes #<id>` in the message trailers to enforce auto-closing via the Git platform conventional messages. If the MCP server crashes (e.g. `Bad Request`) or is disabled, fallback to GitHub CLI (`gh pr create`). You MUST NOT use `helper.sh issue close` or edit `board.md` manually; rely strictly on Git commit trailers to automatically trigger local hooks and close issues.
- **Architectural Reference Blueprints:** Read `.agents/blueprints/` guides (e.g. `clean-architecture.md`, `monorepo.md`) to align on structural layout before planning new architectural components.
- **Human Programmer Mode:** Human developers are granted warning-only bypasses for quality and bureaucratic checks (linting, module locks, etc.).
- **Proactive Skill Loading:** You MUST proactively load the required `SKILL.md` via `view_file` at the start of tasks matching that domain (e.g., `testing`, `engineering-standards`, `security-compliance`, `troubleshooting`). Bypassing required playbook reads is strictly audited and blocks execution.
- **Silent Execution & Final Reporting:** The agent MUST execute tools and commands silently in the background. Do NOT explain your reasoning or actions step-by-step before executing them (e.g., "I will run this command now"). Provide a single summary only when the entire task is completed.
- **Human-in-the-Loop Escalation:** The agent MUST halt and notify the user clearly if it encounters tasks requiring human input (e.g., manual approvals, 2FA, ambiguous choices).

## 5. Plug-and-Play Adaptation & Self-Learning
- **Stack Adaptiveness**: The agent layout is project-agnostic. `./helper.sh bootstrap` (a thin wrapper around `bootstrap.py` — all detection logic lives in the Python script, not duplicated in the shell wrapper, per the no-duplicate-templates rule in `AGENTS.md`) auto-detects and supports any programming language stack (e.g. Python, Node, PHP, Go, Rust, Java, C#) for the *target* project, without strict folder structure constraints.
- **Continuous Self-Learning**: After resolving any bug, workflow issue, or optimization, the agent MUST run `./helper.sh learn "<lesson>"` (optionally with `--category <name>`) to append the lesson in `.agents/memory/lessons-learned.yaml`. Always review this file at the start of work. (Also listed in `AGENTS.md` §3 CLI reference.)
- **Token & Context Efficiency**: The agent SHOULD record found filepaths in its thinking block to minimize token footprint. Repeated calling of search tools (`grep_search`, `list_dir`) or file retrieval for the same paths is allowed when required to perform a deeper analysis, verify workspace state, or confirm modifications.
- **Prompt Caching**: To preserve prompt cache state and save context tokens, reuse retrieved file content and search results from previous turns where possible, but feel free to re-query files or paths to ensure analytical depth and verification correctness.
- **Template & Wrapper Parity**: Before modifying templates, wrappers (bootstrap, install, helper), or generated configs, the agent MUST read `.agents/docs/template_map.md` to ensure exact parity across Linux (Bash) and Windows (PowerShell) platforms, preventing platform-drift and token waste.

## 6. Synthesized Rules (Self-Learning Memory)
- **[Learning: workflow]** ALWAYS use the strict Epic/Task Git branching flow even when modifying agent-internal files like AGENTS.md. DO NOT edit main directly.; ALWAYS run `./helper.sh changelog` and understand SemVer (Major.Minor.Patch) before completing a task to ensure release notes are generated.
- **[Learning: Testing / Mocking]** When mocking `sys.exit`, ALWAYS configure it to raise `SystemExit` (`side_effect=SystemExit`) and wrap in `assertRaises`. Uncontrolled mock exits leak and truncate real local configs.; Validation guard leverages git-diff driven incremental validation to skip static checks/tests on untouched code.
- **[Learning: OS Compatibility / PowerShell]** Maintain exact functional parity between Bash (`.sh`) and PowerShell (`.ps1`) helper scripts.; PowerShell Quirks: Explicitly cast outputs to `[string]` when testing results. Enclose `Test-Path` in parentheses before using `-and`. Propagate `$LASTEXITCODE`.
- **[Learning: General]** Always ensure README.md examples strictly match the python domain entities (GitProfile, Project). Profile credentials (ssh, pat, token) should no longer use encryption.
- **[Learning: diagnostics]** When MCP tools or external CLIs (like 'gh') fail, NEVER just halt with a generic error message. You MUST proactively run diagnostic checks (e.g., testing tokens, checking scopes) and report the exact technical root cause and error logs to the user so they are fully informed of the bottleneck.
