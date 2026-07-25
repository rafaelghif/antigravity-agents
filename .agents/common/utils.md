# Shared Agent Utilities

## 1. Retry Logic
- **Transient Errors**: Retry operations up to `config.json -> retries.network_error_max` times with exponential backoff.
- **Flaky Tests**: Retry failing tests up to `config.json -> retries.flaky_tests_max` times.

## 2. Error Handling & Redaction
- **Log Redaction**: Before writing to `.agents/brain/audit.jsonl`, run content through regex filters to mask API keys, tokens, and secrets. Examples:
  - Bearer tokens: `s/Bearer [a-zA-Z0-9_-]+/Bearer ***/g`
  - AWS Keys: `s/AKIA[0-9A-Z]{16}/AKIA**REDACTED**/g`
  - Database URIs: `s/:\/\/[^:]+:[^@]+@/:\/\/***:\*\*\*@/g`
- **Trace Propagation**: Ensure a generated `trace_id` is appended to all logs across all skill executions to correlate events.

## 2.5 State Management & File I/O
- **Atomic Writes**: Always perform state updates (e.g., `state.json`) atomically to prevent locking and corruption. Write to a temporary file first, then move it: `echo "$DATA" > .agents/brain/state.json.tmp && mv .agents/brain/state.json.tmp .agents/brain/state.json`.

## 3. Framework Detection (Shared)
1. Read current working directory.
2. Check `package.json` for npm/pnpm/yarn (use `workspaces` for monorepos).
3. Check `requirements.txt` for pip.
4. Check `Cargo.toml` for cargo.
5. Check `go.mod` for go.
6. Check `Gemfile` for bundler.

## 4. API Version Negotiation
- Before invoking external tools (e.g., Gitea, GitHub, MCP), verify version compatibility (e.g., `tool --version` or `/api/v1/version`).
- Fallback to safe known API endpoints if the newest API version is unsupported.
