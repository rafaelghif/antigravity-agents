---
name: cavecrew
description: Guides delegation to specialized subagents (investigator, builder, reviewer) with compressed output contracts to save main context window. Use when delegating tasks to subagents or when compressed agent outputs are needed.
---

# Cavecrew: Compressed Subagent Presets for Antigravity

Cavecrew defines three subagent roles dispatched via `invoke_subagent` that emit compressed output to preserve the main conversation context.

## Presets & Antigravity Invocation

| Role | Antigravity Subagent Spec | Best For | Output Shape |
| :--- | :--- | :--- | :--- |
| **`cavecrew-investigator`** | `TypeName: "research"`, `Model: "flash"` | "Where is X defined", "list callers of Y", symbol discovery | `path:line — symbol — note` |
| **`cavecrew-builder`** | `TypeName: "self"`, `Model: "flash"` | Surgical edit, ≤2 files, strict scope | `path:line-range — change. verified: OK` |
| **`cavecrew-reviewer`** | `TypeName: "research"`, `Model: "flash"` | Diff review, bug audit | `path:line: severity: problem. fix.` |

## Antigravity Dispatch Example

```json
invoke_subagent({
  "Subagents": [
    {
      "Role": "cavecrew-investigator: locate auth middleware",
      "TypeName": "research",
      "Model": "flash",
      "Prompt": "Locate auth middleware definition and callers. Output format: path:line — symbol — short note. No fluff."
    }
  ]
})
```

## Output Contracts

**`cavecrew-investigator`**
```text
<Header>:
- path:line — `symbol` — short note
totals: <counts>.
```

**`cavecrew-builder`**
```text
<path:line-range> — <change ≤10 words>.
verified: <re-read OK | mismatch @ path:line>.
```

**`cavecrew-reviewer`**
```text
path:line: <severity>: <problem>. <fix>.
totals: N-critical N-warning N-info
```

## Chaining Patterns

1. **Locate → Fix → Verify**:
   - Step 1: `invoke_subagent` with `Role: "cavecrew-investigator"`, `TypeName: "research"`.
   - Step 2: Main thread passes matched lines to `cavecrew-builder` (`TypeName: "self"`).
   - Step 3: `cavecrew-reviewer` (`TypeName: "research"`) checks the resulting diff.
2. **Parallel Scout**:
   - Spawn multiple investigator subagents concurrently in a single `invoke_subagent` call targeting different subsystems.
