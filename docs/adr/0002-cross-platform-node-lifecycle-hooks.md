# 2. Cross-Platform Node.js Lifecycle Hooks Architecture

Date: 2026-09-14
Status: Accepted

## Context

Google Antigravity executes lifecycle hook commands declared in `.agents/hooks.json` via:
- `cmd /c <command>` on Windows
- `sh -c <command>` on Linux / macOS

If `.agents/hooks.json` binds directly to `powershell -File ...`, the execution will fail on Linux and macOS where PowerShell is not installed by default (`powershell: command not found`). Conversely, invoking `sh ./hook.sh` fails natively on Windows `cmd.exe`.

## Decision

We adopt **Standard Library Node.js Scripts** (`node hooks/<script>.js`) as the single, universal execution driver in `.agents/hooks.json`:

1. **Universal Execution Runtime**: Node.js is universally present in all Antigravity agentic workspaces. Both `cmd /c node ...` and `sh -c node ...` execute identically without shell translation layers.
2. **Zero Dependencies**: All hook scripts rely solely on native Node.js standard modules (`node:fs`, `node:child_process`, `node:process`).
3. **Reference Implementations**: We maintain `.ps1` (PowerShell) and `.sh` (POSIX sh) scripts alongside `.js` in `.agents/hooks/` for developers wanting to test or run hooks manually in their host shells.

## Consequences

- **Positive**: 100% cross-platform parity across Windows, macOS, and Linux with a single `hooks.json`.
- **Positive**: Eliminates duplicate logic and configuration drift across different OS environments.
- **Trade-off**: Requires Node.js in PATH, which is already an inherent dependency for repository test suites and tooling.
