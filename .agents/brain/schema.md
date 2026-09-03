# AAC v4.43.0 State Contracts

## Architecture & Task Lifecycle

1. `intent.yaml`: Top-level architectural declaration with status (`IN_PROGRESS` / `DONE`).
2. `tasks/<id>.yaml`: Atomic micro-tasks with acceptance criteria and execution status.
3. `handoff.json`: Inter-agent state boundary verified via `scripts/neurosymbolic_engine.py`.

## Antigravity Workspace Customizations

- `.agents/agents/<name>.md`: Custom L9 subagents with frontmatter `skills`, `enable_write_tools`, `enable_mcp_tools`, and `enable_subagent_tools`.
- `.agents/skills/<name>/SKILL.md`: Modular domain playbooks with YAML frontmatter `name` and `description`.
- `.agents/mcp_config.json`: Workspace Model Context Protocol configuration.
- `.agents/antigravity-settings.example.json`: Global CLI settings template.

## Verification

- `python3 scripts/verify.py --execute --terse`: Central verification pipeline running all 9 static AST and runtime gates.
- `.githooks/pre-commit`: Local git gate preventing commits with regressions.
