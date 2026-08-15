# Antigravity Agent Core v4.4.4

Compact always-on policy, discoverable Antigravity custom agents, focused skills, and stack-aware verification for reliable AI coding.

[![Version](https://img.shields.io/badge/version-4.4.4-blue.svg)](https://github.com/rafaelghif/antigravity-agents/releases/tag/v4.4.4)
[![Platform](https://img.shields.io/badge/platform-Antigravity_CLI-8A2BE2.svg)](https://antigravity.google/docs/cli/overview)

## Architecture

- `AGENTS.md`: always-on policy, under 600 words.
- `GEMINI.md`: tiny compatibility bootstrap that points to `AGENTS.md`.
- `.agents/agents/`: planner, implementer, reviewer, and security-reviewer.
- `.agents/skills/`: code-quality, verification, security, and architecture.
- `scripts/verify.py`: detects the project stack and available checks.
- `scripts/validate.py`: validates AAC contracts and instruction budgets.
- `.agents/mcp_config.json`: Antigravity workspace MCP configuration.
- `.agents/antigravity-settings.example.json`: sandbox and permission baseline.

## Workflow

Follow official Antigravity best practice:

1. Explore relevant files, symbols, contracts, tests, and stack.
2. Use `/planning` or `--mode plan` for multi-file, architectural, security, or ambiguous work.
3. Execute the smallest correct change in the sandbox.
4. Run `python3 scripts/verify.py`, then every available project check it reports.
5. Review the artifact/diff, error paths, security boundaries, and residual risks.

Use `/agents` for custom agents, `/skills` for loaded skills, `/mcp` for MCP, `/config` and `/permissions` for safety, `/artifact` or `/diff` for review, `/tasks` for background commands, and `/rewind` for course correction. For automation use `agy -p ... --output-format json`.

Workspace skills become custom slash commands automatically. They are not a substitute for `AGENTS.md`.

## Installation

Linux/macOS/WSL:

```bash
curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/v4.4.4/install.sh | bash

```

Windows PowerShell:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; iwr -useb https://raw.githubusercontent.com/rafaelghif/antigravity-agents/v4.4.4/install.ps1 | iex
```

Installers validate before mutation, back up managed files, preserve local state, and run structural validation. Copy `.agents/antigravity-settings.example.json` manually to `~/.gemini/antigravity-cli/settings.json` and adapt permissions to your environment. Note: The `.agents/config.json` file is a custom configuration exclusively read by the `scripts/validate.py` and `scripts/verify.py` scripts, and is not a native Antigravity CLI configuration file.

## Layout

```text
AGENTS.md
CHANGELOG.md
install.sh / install.ps1
scripts/
  validate.py
  verify.py
.agents/
  agents/ planner.md implementer.md reviewer.md security-reviewer.md
  skills/ code-quality.md verification.md security.md architecture.md
  brain/ plans/ common/
  mcp_config.json.example
  antigravity-settings.example.json
  antigravity-compatibility.json
```

`opencode.json` is ignored and optional OpenCode-only configuration. Antigravity CLI uses the `.agents/` workspace surface.

## References

- [Best Practices](https://antigravity.google/docs/cli/best-practices)
- [Plugins and Skills](https://antigravity.google/docs/cli/plugins)
- [Subagents](https://antigravity.google/docs/cli/subagents)
- [MCP](https://antigravity.google/docs/cli/mcp)
- [Permissions and Sandbox](https://antigravity.google/docs/cli/permissions)
- [Headless Mode](https://antigravity.google/docs/cli/headless)
