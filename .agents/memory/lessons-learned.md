# AAC V3 Lessons Learned

This file logs project-wide incident reports, testing optimizations, and workflow patterns learned from development sessions.

## 1. Workflow & Rules Compliance
- **[2026-07-17] Git Flow**: ALWAYS use the strict Epic/Task Git branching flow even when modifying agent-internal files like `AGENTS.md`. DO NOT edit `main` directly.
- **[2026-07-17] SemVer**: ALWAYS run `./helper.sh changelog` and understand SemVer (Major.Minor.Patch) before completing a task to ensure release notes are generated.
- **[2026-07-16] Skill Enforcer**: AI Skill Enforcer strictly blocks validation if required playbooks (e.g. `devops-release`) were not viewed when modifying related files.
- **[2026-07-11] Skill Evolution**: Dynamically scaffold and index custom playbooks using CLI skill tools to extend agent capabilities whenever facing domain-specific task gaps.

## 2. Configuration, MCP & Workspace Setup
- **[2026-07-14] Template Parity**: Replaced regex replacements with static `.template` files for config generation. Always sync template-to-target files (mapped in `template_map.md`) to prevent drift.
- **[2026-07-14] MCP Setup**: MCP servers are centralized in `mcp_config.json.template` (supporting local domains and tokens) and Git profiles in `.agents/git_profiles.json`.
- **[2026-07-11] Security**: Harden Git hooks, sanitize user SSH keys, and enforce Git source downloading for offline compatibility.

## 3. Token Budget & Context Optimization
- **[2026-07-04] Budget Parsing**: Platform token limit usage parsing is optimized to extract from markdown tables and lists.
- **[2026-07-04] Async Sync**: Token usage sync executes as a detached background subprocess (using Popen with `start_new_session`) to prevent blocking the user.
- **[2026-06-27] Context Ranges**: Always specify file read ranges to save context tokens. Use targeted context optimization to minimize prompt token footprint.

## 4. Testing, Mocking & Validation
- **[2026-07-02] Python Mocks**: When mocking `sys.exit`, ALWAYS configure it to raise `SystemExit` (`side_effect=SystemExit`) and wrap in `assertRaises`. Uncontrolled mock exits leak and truncate real local configs.
- **[2026-06-28] Incremental Linting**: Validation guard leverages git-diff driven incremental validation to skip static checks/tests on untouched code.

## 5. OS Compatibility (Windows/Linux)
- **[2026-07-04] Parity**: Maintain exact functional parity between Bash (`.sh`) and PowerShell (`.ps1`) helper scripts.
- **[2026-06-28] PowerShell Quirks**: Explicitly cast outputs to `[string]` when testing results. Enclose `Test-Path` in parentheses before using `-and`. Propagate `$LASTEXITCODE`.
- **[2026-07-02] Python Encoding**: Reconfigure `sys.stdout` to utf-8, use cross-platform path resolution, and specify `encoding='utf-8'` on `subprocess.run` calls.

## Lessons Learned
- **[2026-07-17]** **Path Handling / OS Compatibility**: Use cross-platform path resolution helpers instead of hardcoded OS separators to prevent Windows/Linux path mismatches.
