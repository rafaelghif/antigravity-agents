# AAC V2 Lessons Learned

This file logs project-wide incident reports, testing optimizations, and workflow patterns learned from development sessions.

## Lessons Learned
- **[2026-07-04]** **token-budget**: Implemented automatic platform token usage sync by executing agy -p "/usage" and parsing the output (table, list, and console text formats) robustly via regex, avoiding infinite recursion via INTERNAL_SYNC environment guards, and improving active account detection via ~/.gemini/google_accounts.json.
- **[2026-07-04]** **token-audit**: Supported per-account token budget tracking in token.py by dynamically detecting active profile from git_profiles.json
- **[2026-07-04]** **token-audit**: Implemented a strict local token budget tracker and logging CLI subcommand 'token' supporting log, status, and reset, including dynamic date-based resets and branch-based task auto-detection
- **[2026-07-04]** **Database Schema**: Strictly align API and database models with the project schemas to maintain interface integrity.
- **[2026-07-04]** **documentation**: Fixed installer repository raw.githubusercontent.com URLs in README.md from rafaelghifari to rafaelghif
- **[2026-07-04]** **installation**: Enforce Git source repository downloading for all installations, bootstrapping, and upgrades, and mock git clone in tests to preserve offline compatibility.
- **[2026-07-04]** **Testing**: When testing validation of critical files, ensure unit tests mock all JSON schema lookups (like validate_json_schema) to avoid test failures when untracked transient configuration files like locks.json are deleted.
- **[2026-07-04]** **Context / Token Optimization**: Use targeted context optimization to minimize prompt token footprint while preserving compliance with rules.
- **[2026-07-02]** **Testing / Mocking**: Ensure mock side effects are isolated and sys.exit mocks raise SystemExit to prevent uncontrolled test discovery side-effects.
- **[2026-07-02]** **Path Handling / OS Compatibility**: Use cross-platform path resolution helpers instead of hardcoded OS separators to prevent Windows/Linux path mismatches.
- **[2026-07-02]** **Git Profile & Credentials**: Validate GPG key imports and developer identity rotation rules locally to safeguard credentials.
- **[2026-07-02]** **git**: Prevent applying placeholder Git profiles to local Git config when user-defined profiles are unconfigured, avoiding pollution of local Git author config
- **[2026-07-02]** **compatibility**: Always reconfigure sys.stdout and sys.stderr to utf-8, handle ValueError on os.path.relpath cross-drive matches, propagate exit codes using exit $LASTEXITCODE in PowerShell wrapper scripts, and specify encoding='utf-8' on subprocess.run calls to ensure complete Windows compatibility.
- **[2026-06-28]** **powershell**: Explicitly cast command and function outputs to [string] when matching or testing results in PowerShell to prevent type casting bugs on non-standard PowerShell environments.
- **[2026-06-28]** **powershell**: Avoid using the -and operator directly after Test-Path in PowerShell without enclosing Test-Path in parentheses, otherwise PowerShell parses -and as a parameter to Test-Path.
- **[2026-06-28]** **performance**: Leverage git-diff driven incremental validation in validation guard to skip syntax and unit tests checks when code is untouched, optimizing validation run speed.
- **[2026-06-28]** **security**: Harden git credentials tracking by explicitly ignoring git_profiles.json in configuration rules, and silence validation warnings by adding silent flags to git_api helpers.
- **[2026-06-28]** **installer**: Ensure robust Git hooks path resolution in subdirectories and monorepos by using git rev-parse --git-path hooks and --show-prefix, and avoid strict-mode property access crashes in PowerShell.
- **[2026-06-27]** **Token Efficiency**: Always specify file read ranges to save context tokens.
- **[2026-06-27]** **V2 Restructuring**: Maintain a flat and modular directory structure to simplify agent context parsing and increase model prompt cache efficiency.
- **[2026-06-27]** **Python Mock Leaks**: When mocking `sys.exit` in Python unit tests, configure it to raise `SystemExit` (using `side_effect=SystemExit`) and wrap the calls in `assertRaises(SystemExit)`. Uncontrolled mock exits allow the test execution to proceed past the exit point, potentially causing side-effects such as truncating or corrupting real local configuration files during test discover suites.
