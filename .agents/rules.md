# AAC V2 Project Rules

These rules extend the core guidelines in `AGENTS.md` with project-specific language and tool specifications.

> **Scope note:** Section 1–3 below govern **AAC's own source code** (the CLI tool itself, which is built in Python). They do **not** apply to whatever stack a *managed/target* project uses — that's handled by the stack-agnostic detection described in Section 4.

## 1. Programming Language & Tools (AAC's own codebase)
- Use **Python 3** for the main product stack.
- Rely on the standard library where possible to minimize external dependencies.
- Use **Bash** for lightweight POSIX-compatible wrapper scripts. Ensure path-separators and directory check logic are safe for multi-platform execution (e.g. using `python3` wrappers on Windows).

## 2. Style Guidelines & Linting
- Follow **PEP 8** style guidelines for all Python code.
- Always include clear docstrings for public classes, modules, and functions.
- Keep functions short, focused, and under 50 lines where practical.

## 3. Testing Requirements
- Every new feature or command module MUST have corresponding unit tests under `tests/`.
- Tests must use standard `unittest` or `pytest` frameworks.
- Mock all filesystem or external command calls to ensure tests remain deterministic and fast.

## 4. Plug-and-Play Adaptation & Self-Learning
- **Stack Adaptiveness**: The agent layout is project-agnostic. `./helper.sh bootstrap` (a thin wrapper around `bootstrap.py` — all detection logic lives in the Python script, not duplicated in the shell wrapper, per the no-duplicate-templates rule in `AGENTS.md`) auto-detects and supports any programming language stack (e.g. Python, Node, PHP, Go, Rust, Java, C#) for the *target* project, without strict folder structure constraints.
- **Continuous Self-Learning**: After resolving any bug, workflow issue, or optimization, the agent MUST run `./helper.sh learn "<lesson>"` (optionally with `--category <name>`) to append the lesson in `.agents/memory/lessons-learned.md`. Always review this file at the start of work. (Also listed in `AGENTS.md` §3 CLI reference.)

## 5. Synthesized Rules (Self-Learning Memory)
- **[Learning: compatibility]** Always reconfigure sys.stdout and sys.stderr to utf-8, handle ValueError on os.path.relpath cross-drive matches, propagate exit codes using exit $LASTEXITCODE in PowerShell wrapper scripts, and specify encoding='utf-8' on subprocess.run calls to ensure complete Windows compatibility.
- **[Learning: powershell]** Explicitly cast command and function outputs to [string] when matching or testing results in PowerShell to prevent type casting bugs on non-standard PowerShell environments.
- **[Learning: powershell]** Avoid using the -and operator directly after Test-Path in PowerShell without enclosing Test-Path in parentheses, otherwise PowerShell parses -and as a parameter to Test-Path.
- **[Learning: feature]** Implemented local visual web dashboard server, structured VS Code extension integration logic, and registered conversational skill playbooks to unify agent operations.
- **[Learning: performance]** Implemented Git-diff driven incremental validation in validation guard to skip syntax and unit tests checks when code is untouched.
- **[Learning: docs]** Synchronized README.md instructions and CLI references with PowerShell autocomplete and shell completion capabilities.
- **[Learning: feature]** Unified API credentials fallback to profile configs, integrated GPG keyring auditing into doctor diagnostics, implemented PowerShell autocomplete support, and automated lock releases inside the staging phase of issue closures.
- **[Learning: security]** Hardened git credentials tracking by explicitly ignoring git_profiles.json in configuration rules, and silenced validation warnings by adding silent flags to git_api helpers.
- **[Learning: installer]** Ensured robust Git hooks path resolution in subdirectories and monorepos by using git rev-parse --git-path hooks and --show-prefix, and fixed strict-mode property access crashes in PowerShell.
- **[Learning: Token Efficiency]** Always specify file read ranges to save context tokens
- **[Learning: V2 Restructuring]** Moving to a flat and modular directory structure simplifies agent context parsing and increases model prompt cache efficiency.
- **[Learning: Python Mock Leaks]** When mocking `sys.exit` in Python unit tests, configure it to raise `SystemExit` (using `side_effect=SystemExit`) and wrap the calls in `assertRaises(SystemExit)`. Uncontrolled mock exits allow the test execution to proceed past the exit point, potentially causing side-effects such as truncating or corrupting real local configuration files during test discover suites.
