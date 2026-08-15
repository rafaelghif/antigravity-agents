# AAC v4.4.2 — Always-On Workspace Policy

This file is the compact workspace policy for Antigravity CLI. Follow it before editing. Detailed procedures are opt-in skills under `.agents/skills/` and custom agents under `.agents/agents/`.

## Core Rules

1. **Explore first.** Inspect the relevant files, symbols, contracts, and existing tests before proposing edits. Never invent APIs, fields, dependencies, or test commands.
2. **Plan proportional to risk.** Use `--mode plan` or `/planning` for multi-file, architectural, security, or ambiguous work. T1 changes may proceed directly.
3. **Make the smallest correct change.** Preserve existing behavior unless the request explicitly changes it. Avoid unrelated refactors and compatibility shims.
4. **Use the right specialist.** Choose a custom agent or skill only when its trigger matches the task. Do not load every skill for every request.
5. **Verify before claiming completion.** Detect the project stack, run its available formatter/linter/tests, validate the diff, and report commands that do not exist as `not available`.
6. **Review the result.** Inspect the final diff, changed files, error paths, security boundaries, and residual risks. A green command is not proof of correct behavior.
7. **Protect the workspace.** Use the Antigravity sandbox and review permissions. Ask before destructive commands, credential access, migrations, releases, or remote mutations.
8. **Keep state honest.** Update one active plan only when the task needs one. A completed plan is archived and never resumed. Git history and remote PRs are the delivery record.
9. **Communicate concisely.** State the finding, action, verification result, and blocker. Do not narrate routine reads or repeat persona language.

## Definition Of Done

- Full relevant context was inspected.
- Contracts and existing behavior were preserved or intentionally changed.
- Tests/checks were added or the gap was reported.
- Available formatter, linter, type checker, and tests were run.
- Final diff and security/error paths were reviewed.
- Residual risks and exact verification output were reported.

## Delivery

Use normal Antigravity `explore -> plan -> execute -> verify -> review` for coding. Use the repository's issue/branch/PR/release policy for remote delivery. Do not let Git ceremony replace engineering verification.

## Workspace References

- `.agents/agents/`: explicit planner, implementer, reviewer, and security agents.
- `.agents/skills/`: concise task-specific checklists, loaded only when relevant.
- `.agents/mcp_config.json`: Antigravity workspace MCP configuration.
- `.agents/antigravity-settings.example.json`: sandbox and permission baseline.
- `scripts/verify.py`: stack-aware verification.
