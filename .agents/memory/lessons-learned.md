# AAC V3 Lessons Learned

This file logs project-wide incident reports, testing optimizations, and workflow patterns learned from development sessions.

## Lessons Learned
- **[2026-07-14]** **mcp**: Synchronized target workspace and global registration formats for MCP servers (adding disabled and alwaysAllow fields) to maintain schema alignment.
- **[2026-07-14]** **installation**: Isolated target installations by excluding wrapper scripts (bootstrap/install) and customized AGENTS.md rules in target projects to avoid agent self-repair leaks.
- **[2026-07-11]** **git**: Documented prompt expansion and human approval flows in AGENTS.md, resolved git branch validation enforcer error due to missing feat prefix by amending git commit message.
- **[2026-07-11]** **Skill Evolution / Self-Improvement**: Dynamically scaffold and index custom playbooks using CLI skill tools to extend agent capabilities whenever facing domain-specific task gaps.
- **[2026-07-11]** **security**: Hardened CLI profile keys and bootstrap process by sanitizing user-provided SSH key path via validation regex against shell command injections and implementing offline bootstrapper templates fallback directory checks.
- **[2026-07-11]** **documentation**: Documented comprehensive setup steps for Git profiles, monorepo configuration projects.json, and MCP servers (local and remote/Gitea) in README.md.
- **[2026-07-11]** **configuration**: Configured and integrated Gitea Docker-based MCP server configuration supporting custom local domains and tokens into mcp_config.json.
- **[2026-07-11]** **configuration**: Integrated GitHub API MCP server configuration inside mcp_config.json and appended .agents/git_profiles.json rotation and monorepo project configurations mapping to template_map.md.
- **[2026-07-11]** **configuration**: Documented config template-to-target file relationships and Linux/Windows CLI wrapper parity to prevent drift, resolved rules sync duplication bugs, and secured mcp_server path registry.
- **[2026-07-11]** **reconnaissance**: Decoupled modular stack detectors in recon.py to dynamically adapt test/build commands and frameworks (e.g., C# WinForms/WPF/Web, PHP Pest/PHPUnit, Ruby RSpec) across all major programming ecosystems.
- **[2026-07-04]** **Shell Scripting**: Maintain parity between Bash (.sh) and PowerShell (.ps1) helper scripts for consistent developer experience across platforms.
- **[2026-07-04]** **token-budget**: Optimized scan_conversations_for_usage to read JSONL transcripts first and enforced a strict 5-minute age validation for both transcript and DB steps. Prevented dynamic limits overrides when limits are parsed directly from Markdown tables, saved direct used overrides, and implemented dynamic freshness check in run_status to trigger async background sync when budget is older than 2 minutes.
- **[2026-07-04]** **token-budget**: Fixed platform usage parser to correctly parse limits and used tokens from Markdown table column format and support bullet lists (*) and bold tags (**) in account/task breakdowns.
- **[2026-07-04]** **token-budget**: Optimized token logging latency by spawning the platform sync process as a detached background subprocess (using Popen with start_new_session/CREATE_NEW_PROCESS_GROUP), eliminating the 3-5 seconds user blocking wait.
- **[2026-07-04]** **token-budget**: Fixed rolling window token quotas parsing from platform /usage command by implementing multi-line block extraction (avoiding fragile line+1 checks), and added remaining tokens calculation/display to the token status CLI command.
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
