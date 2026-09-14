# cavecrew

Decision guide: when to delegate to Antigravity subagents (`invoke_subagent`) instead of doing the work inline in the main context.

## What it does

Guides the primary agent when to spawn specialized subagents with compressed output contracts to protect the main conversation context window.

Three subagent roles:

| Subagent Role | Antigravity Type | Job | Use when |
| :--- | :--- | :--- | :--- |
| `cavecrew-investigator` | `TypeName: "research"`, `Model: "flash"` | Locate code (read-only) | "Where is X defined / what calls Y / list uses of Z" |
| `cavecrew-builder` | `TypeName: "self"`, `Model: "flash"` | Surgical edit, 1-2 files | Scope is obvious, ≤2 files. Refuses 3+ file scope. |
| `cavecrew-reviewer` | `TypeName: "research"`, `Model: "flash"` | Diff/file review | One-line findings with severity tags |

Use main thread directly for one-line answers and 3+ file architectural refactors.

## How to invoke

Triggers on user phrases like "delegate to subagent", "use cavecrew", "spawn investigator", "save context", "compressed agent output".

## Chaining Pattern

Locate → fix → verify (most common):

1. `cavecrew-investigator` returns site list (`path:line`, symbol, note) via `invoke_subagent`.
2. Main thread picks 1-2 sites, hands paths to `cavecrew-builder`.
3. `cavecrew-reviewer` audits the resulting diff.

Parallel scout: spawn 2-3 `cavecrew-investigator` subagents in one concurrent `invoke_subagent` call with different angles (definitions, callers, tests). Aggregate in main.

## Model Selection

In Google Antigravity, subagents support:
- `flash` (default for fast lookups and small edits)
- `pro` (for complex architectural reasoning)
- `inherit` (inherits parent session model)

## See also

- [`SKILL.md`](./SKILL.md): full decision matrix and invocation contracts
- [AGENTS.md](../../../AGENTS.md): workspace root guidelines
