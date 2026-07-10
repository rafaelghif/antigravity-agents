# AAC V3 Context Map & CLI Reference

This document maps workspace files and details the CLI helper commands.

## 1. CLI Helper Commands Reference
All operations must be performed using `./helper.sh` (Linux/macOS) or `./helper.ps1` (Windows):
- `./helper.sh bootstrap`: Scaffolds dirs, stack detect, AGENTS.md, profile wizard.
- `./helper.sh validate`: Runs 10 audits (critical files, secrets, links, branch, sync, task board, lint, tests, locks, commits).
- `./helper.sh issue <create|list|checkout|close|sync>`: Subtask and issue lifecycle tracking.
- `./helper.sh lock <module-name>`: Acquires local locks. Unlock with `--release <module-name>`.
- `./helper.sh profile <add|switch|list|apply>`: Credentials rotation and auto-sync config.
- `./helper.sh changelog`: Conventional commits parser and SemVer version bump.
- `./helper.sh sync`: Updates skills and ADR registries.
- `./helper.sh learn "<lesson>" [--category <name>]`: Appends a lesson to `.agents/memory/lessons-learned.md` after resolving a bug or workflow issue.
- `./helper.sh heartbeat`: Runs workspace heartbeat diagnostic checks (verifies locks, hooks, budget).

## 2. Context map — what loads when

| Path | Contents | When it loads |
|---|---|---|
| `AGENTS.md` | Identity, non-negotiables | Always — every prompt |
| `.agents/rules.md` | Project-specific stack, style, and testing rules (language, lint, frameworks) | Always — loaded alongside `AGENTS.md` every prompt |
| `.agents/skills/adr/SKILL.md` | Standardized playbook and template for generating new Architectural Decision Records. | On match |
| `.agents/skills/ci-cd/SKILL.md` | Playbook for setting up CI/CD pipelines, automating linting, testing, building, caching, and staging release gates. | On match |
| `.agents/skills/code-review/SKILL.md` | Guidelines and checklists for performing high-quality, zero-regression code reviews. | On match |
| `.agents/skills/coding-standards/SKILL.md` | Principles, workflows, and standards for writing clean, secure, and highly optimized code, including guidelines for code writing, code review, and architectural integrity. | On match |
| `.agents/skills/contract-synchronization/SKILL.md` | Playbook for managing API contract schemas, generating client code, and verifying backend/frontend synchronization. | On match |
| `.agents/skills/conversational-agent/SKILL.md` | Playbook for translating natural language requests about tasks, profiles, locking, and validation into CLI helper executions. | On match |
| `.agents/skills/database-evolution/SKILL.md` | Playbook for writing safe database migrations, managing schema evolutions, executing reversible rollbacks, and avoiding table lock contention in enterprise environments. | On match |
| `.agents/skills/debugging/SKILL.md` | Diagnostic playbook for troubleshooting CLI errors, shell script crashes, and test failures. | On match |
| `.agents/skills/observability/SKILL.md` | Guidelines for implementing structured logging, distributed tracing (OpenTelemetry), performance metrics, and centralized error telemetry. | On match |
| `.agents/skills/performance-optimization/SKILL.md` | Guidelines for CPU profiling, identifying database query bottlenecks (N+1 queries), diagnosing memory leaks, and optimizing resource execution speeds. | On match |
| `.agents/skills/release-management/SKILL.md` | Guidelines for containerization (Dockerfile best practices), release versioning, blue-green deployment, feature flag rollouts, and post-deployment smoke verification. | On match |
| `.agents/skills/security-audit/SKILL.md` | Diagnostic playbook for scanning vulnerabilities, verifying secret exclusion, and executing OWASP Top 10 compliance audits. | On match |
| `.agents/skills/self-healing/SKILL.md` | Diagnostic and recovery playbook for resolving local git states, locked configuration files, broken workspace setups, and process deadlocks. | On match |
| `.agents/skills/skill-evolution/SKILL.md` | Playbook instructing agents how to dynamically formulate, design, bootstrap, and register new workspace skills when facing skill gaps. | On match |
| `.agents/skills/task-management/SKILL.md` | Playbook for capturing design alignment from /grill-me, generating issue specifications, and managing task boards. | On match |
| `.agents/skills/testing/SKILL.md` | Playbook for executing unit and integration tests, mocking external services, and structuring test suites. | On match |
| `.agents/workflows/*.md` | Slash-command macros (e.g. `/sync-memory`) | Only when the command is run |
| `.agents/memory/architecture.md` | Compressed system summary | Pulled on demand (`@.agents/memory/architecture.md`) before architecture-affecting work |
| `.agents/memory/decisions/` | ADRs — full reasoning | On demand |
| `.agents/memory/glossary.md` | Domain terms | On demand when unfamiliar terms appear |
| `.agents/memory/tech-debt.md`, `lessons-learned.md` | Known shortcuts, past incidents | On demand before related work; appended after the fact |
| `.agents/memory/soul.md` | Core agent values, communication policies, and identity. | Always — loaded alongside `AGENTS.md` every prompt |
| `.agents/tasks/board.md` | Task board | Read at the start of every task, written at every status change |
