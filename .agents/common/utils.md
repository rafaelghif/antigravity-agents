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

## 2.5 State Management, File I/O & POSIX Directory Locks
- **Atomic Writes & Plan Backup Protection**: Always perform file updates atomically. When modifying `.agents/plans/<task-slug>.md`, maintain an automatic `.bak` copy (`cp plan.md plan.md.bak`). If a crash occurs mid-write and `plan.md` becomes corrupted, restore immediately from `plan.md.bak`.
- **POSIX Directory-Based Mutex Locks**: To prevent TOCTOU race conditions across parallel subagents, DO NOT use JSON file writes for locking. Use atomic directory creation: `mkdir -p .agents/locks/<file_hash>.lock`.
  - Inside the lock directory, write a metadata file `owner.json` containing `{"claimed_by": "<agent_id>", "claimed_at": "<ISO8601>"}`.
  - Locks older than `config.json -> state_management.lock_timeout_seconds` (60s) MUST be pruned automatically to release orphan locks safely.



## 3. Universal Polyglot Framework & Language Detection
1. Read current working directory and inspect project tree.
2. **JavaScript / TypeScript / Node.js**: Check `package.json` (npm, pnpm, yarn, bun, workspaces).
3. **Python**: Check `pyproject.toml`, `requirements.txt`, `Pipfile`, `environment.yml`.
4. **Go**: Check `go.mod`.
5. **Rust**: Check `Cargo.toml`.
6. **PHP**: Check `composer.json`.
7. **Java / Kotlin**: Check `pom.xml`, `build.gradle`, `build.gradle.kts`.
8. **C# / .NET / VB.NET**: Check `*.csproj`, `*.vbproj`, `*.sln`.
9. **Dart / Flutter**: Check `pubspec.yaml`.
10. **Ruby**: Check `Gemfile`.
11. **C / C++**: Check `CMakeLists.txt`, `Makefile`, `configure.ac`.
12. **Legacy ASP / VB6 / Classic Systems**: Check `*.asp`, `*.vbp`, `*.bas`, `*.cls`, `web.config`.
13. **Swift / Objective-C**: Check `Package.swift`, `*.xcodeproj`, `Podfile`.
14. **Elixir / Erlang**: Check `mix.exs`, `rebar.config`.

## 3.5 Specific Framework Adaptation Rules
- **Frontend Stack**: Inspect dependencies for `react` / `next`, `vue` / `nuxt`, `angular`, `svelte` / `sveltekit`. Load component purity & hydration guidelines.
- **Python Backend**: Detect `django`, `fastapi`, `flask`. Enforce ORM transaction safety and async loop handling.
- **Node.js Backend**: Detect `express`, `nestjs`, `fastify`. Enforce middleware error bounds and dependency injection patterns.
- **Java / .NET Enterprise**: Detect `spring-boot` or `Microsoft.AspNetCore`. Enforce tier isolation and connection pool management.



## 4. API Version Negotiation
- Before invoking external tools (e.g., Gitea, GitHub, MCP), verify version compatibility (e.g., `tool --version` or `/api/v1/version`).
- Fallback to safe known API endpoints if the newest API version is unsupported.
