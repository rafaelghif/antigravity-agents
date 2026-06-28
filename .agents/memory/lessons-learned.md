# AAC V2 Lessons Learned

This file logs project-wide incident reports, testing optimizations, and workflow patterns learned from development sessions.

## Lessons Learned
- **[2026-06-28]** **powershell**: Avoid using the -and operator directly after Test-Path in PowerShell without enclosing Test-Path in parentheses, otherwise PowerShell parses -and as a parameter to Test-Path.
- **[2026-06-28]** **feature**: Implemented local visual web dashboard server, structured VS Code extension integration logic, and registered conversational skill playbooks to unify agent operations.
- **[2026-06-28]** **performance**: Implemented Git-diff driven incremental validation in validation guard to skip syntax and unit tests checks when code is untouched.
- **[2026-06-28]** **docs**: Synchronized README.md instructions and CLI references with PowerShell autocomplete and shell completion capabilities.
- **[2026-06-28]** **feature**: Unified API credentials fallback to profile configs, integrated GPG keyring auditing into doctor diagnostics, implemented PowerShell autocomplete support, and automated lock releases inside the staging phase of issue closures.
- **[2026-06-28]** **security**: Hardened git credentials tracking by explicitly ignoring git_profiles.json in configuration rules, and silenced validation warnings by adding silent flags to git_api helpers.
- **[2026-06-28]** **installer**: Ensured robust Git hooks path resolution in subdirectories and monorepos by using git rev-parse --git-path hooks and --show-prefix, and fixed strict-mode property access crashes in PowerShell.
- **[2026-06-27]** **Token Efficiency**: Always specify file read ranges to save context tokens
- **V2 Restructuring**: Moving to a flat and modular directory structure simplifies agent context parsing and increases model prompt cache efficiency.
- **Python Mock Leaks**: When mocking `sys.exit` in Python unit tests, configure it to raise `SystemExit` (using `side_effect=SystemExit`) and wrap the calls in `assertRaises(SystemExit)`. Uncontrolled mock exits allow the test execution to proceed past the exit point, potentially causing side-effects such as truncating or corrupting real local configuration files during test discover suites.
