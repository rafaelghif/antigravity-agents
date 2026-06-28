# AAC V2 Lessons Learned

This file logs project-wide incident reports, testing optimizations, and workflow patterns learned from development sessions.

## Lessons Learned
- **[2026-06-28]** **installer**: Ensured robust Git hooks path resolution in subdirectories and monorepos by using git rev-parse --git-path hooks and --show-prefix, and fixed strict-mode property access crashes in PowerShell.
- **[2026-06-27]** **Token Efficiency**: Always specify file read ranges to save context tokens
- **V2 Restructuring**: Moving to a flat and modular directory structure simplifies agent context parsing and increases model prompt cache efficiency.
- **Python Mock Leaks**: When mocking `sys.exit` in Python unit tests, configure it to raise `SystemExit` (using `side_effect=SystemExit`) and wrap the calls in `assertRaises(SystemExit)`. Uncontrolled mock exits allow the test execution to proceed past the exit point, potentially causing side-effects such as truncating or corrupting real local configuration files during test discover suites.
