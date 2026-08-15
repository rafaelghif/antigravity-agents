# AAC v4.4.11 State Contracts

## Active Plan

`.agents/plans/<slug>.md` is optional for T1 work and required for multi-file/architectural work. It contains `## Decisions` and a `## Tasks` checklist. Only one active plan may exist. Completed plans are archived or deleted.

## Antigravity Files

- `.agents/agents/<name>.md`: custom agent with YAML frontmatter `name`, `description`, and `mode`. Use `subagent: true` only when the installed CLI supports that field.
- `.agents/skills/<name>.md`: concise skill with YAML frontmatter `name` and `description`.
- `.agents/mcp_config.json`: workspace MCP config using `mcpServers`; remote servers use `serverUrl`.
- `.agents/antigravity-settings.example.json`: global settings example; copy manually to the Antigravity settings path.

## Verification

`python3 scripts/verify.py` detects the stack and reports checks. Configuration-only repositories use structural validation.
- **Stack Awareness**: Restrict commands to explicitly verified executables from the active workspace context.
