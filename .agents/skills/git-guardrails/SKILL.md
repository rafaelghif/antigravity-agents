---
name: git-guardrails
description: >-
  Sets up Antigravity PreToolUse lifecycle hooks to intercept and block destructive git commands
  (push, reset --hard, clean -f, branch -D, restore .) before run_command executes. Use when the user
  wants git safety guardrails in workspace hooks.json.
---

# Antigravity Git Guardrails

Sets up a `PreToolUse` lifecycle hook in `hooks.json` to block destructive git operations before `run_command` executes.

## Blocked Operations

- `git push` (all variants including `--force`)
- `git reset --hard`
- `git clean -f` / `git clean -fd`
- `git branch -D`
- `git checkout .` / `git restore .`

When blocked, the hook returns `{"decision": "deny", "reason": "..."}` on stdout, cleanly rejecting the tool call before terminal execution.

## Setup Instructions

### 1. Copy Script to Hooks Directory

Copy the guardrail script into `.agents/hooks/`:

- **Windows (PowerShell)**: `.agents/hooks/block-dangerous-git.ps1`
- **Cross-Platform / Node**: `.agents/hooks/block-dangerous-git.js`

### 2. Configure `.agents/hooks.json`

Add the `PreToolUse` hook definition:

```json
{
  "git-guardrails": {
    "enabled": true,
    "PreToolUse": [
      {
        "matcher": "run_command",
        "hooks": [
          {
            "type": "command",
            "command": "powershell -NoProfile -ExecutionPolicy Bypass -File .agents/hooks/block-dangerous-git.ps1",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

*For environments running Node.js:*
```json
{
  "git-guardrails": {
    "enabled": true,
    "PreToolUse": [
      {
        "matcher": "run_command",
        "hooks": [
          {
            "type": "command",
            "command": "node .agents/hooks/block-dangerous-git.js",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
```

### 3. Verification

Test by passing JSON via stdin:

```powershell
'{"toolCall":{"name":"run_command","args":{"CommandLine":"git push origin main"}}}' | powershell -NoProfile -ExecutionPolicy Bypass -File .agents/skills/git-guardrails/scripts/block-dangerous-git.ps1
```

Expected stdout:
```json
{"decision":"deny","reason":"BLOCKED: 'git push origin main' matches dangerous git pattern '\\bgit\\s+push\\b'. Execution blocked by Antigravity git-guardrails."}
```
