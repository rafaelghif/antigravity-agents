# AAC V3 Lessons Learned

This file logs project-wide incident reports, testing optimizations, and workflow patterns learned from development sessions.

## Lessons Repository

<lesson category="workflow" date="2026-07-17">
ALWAYS use the strict Epic/Task Git branching flow even when modifying agent-internal files like `AGENTS.md`. DO NOT edit `main` directly.
</lesson>

<lesson category="workflow" date="2026-07-17">
ALWAYS run `./helper.sh changelog` and understand SemVer (Major.Minor.Patch) before completing a task to ensure release notes are generated.
</lesson>

<lesson category="compliance" date="2026-07-16">
AI Skill Enforcer strictly blocks validation if required playbooks (e.g. `devops-release`) were not viewed when modifying related files.
</lesson>

<lesson category="skills" date="2026-07-11">
Dynamically scaffold and index custom playbooks using CLI skill tools to extend agent capabilities whenever facing domain-specific task gaps.
</lesson>

<lesson category="configuration" date="2026-07-14">
Replaced regex replacements with static `.template` files for config generation. Always sync template-to-target files (mapped in `template_map.md`) to prevent drift.
</lesson>

<lesson category="configuration" date="2026-07-14">
MCP servers are centralized in `mcp_config.json.template` (supporting local domains and tokens) and Git profiles in `.agents/git_profiles.json`.
</lesson>

<lesson category="security" date="2026-07-11">
Harden Git hooks, sanitize user SSH keys, and enforce Git source downloading for offline compatibility.
</lesson>

<lesson category="security" date="2026-07-17">
Validate GPG key imports and developer identity rotation rules locally to safeguard credentials.
</lesson>

<lesson category="optimization" date="2026-07-04">
Platform token limit usage parsing is optimized to extract from markdown tables and lists.
</lesson>

<lesson category="optimization" date="2026-07-04">
Token usage sync executes as a detached background subprocess (using Popen with `start_new_session`) to prevent blocking the user.
</lesson>

<lesson category="optimization" date="2026-06-27">
Always specify file read ranges to save context tokens. Use targeted context optimization to minimize prompt token footprint.
</lesson>

<lesson category="testing" date="2026-07-02">
When mocking `sys.exit`, ALWAYS configure it to raise `SystemExit` (`side_effect=SystemExit`) and wrap in `assertRaises`. Uncontrolled mock exits leak and truncate real local configs.
</lesson>

<lesson category="testing" date="2026-06-28">
Validation guard leverages git-diff driven incremental validation to skip static checks/tests on untouched code.
</lesson>

<lesson category="compatibility" date="2026-07-04">
Maintain exact functional parity between Bash (`.sh`) and PowerShell (`.ps1`) helper scripts.
</lesson>

<lesson category="compatibility" date="2026-06-28">
PowerShell Quirks: Explicitly cast outputs to `[string]` when testing results. Enclose `Test-Path` in parentheses before using `-and`. Propagate `$LASTEXITCODE`.
</lesson>

<lesson category="compatibility" date="2026-07-02">
Python Encoding: Reconfigure `sys.stdout` to utf-8, use cross-platform path resolution, and specify `encoding='utf-8'` on `subprocess.run` calls.
</lesson>

<lesson category="compatibility" date="2026-07-17">
Path Handling / OS Compatibility: Use cross-platform path resolution helpers instead of hardcoded OS separators to prevent Windows/Linux path mismatches.
</lesson>
