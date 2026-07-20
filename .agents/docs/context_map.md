# AAC V3 Context Map & CLI Reference

This document maps workspace files and details the CLI helper commands.

## 1. CLI Helper Commands Reference
All operations must be performed using `./helper.sh` (Linux/macOS) or `./helper.ps1` (Windows):
- `./helper.sh bootstrap [-q | --quick]`: Scaffolds dirs, stack detect, AGENTS.md, profile wizard. `--quick` runs zero-config setup using defaults.
- `./helper.sh validate [-q | --quiet]`: Runs 11 audits (critical files, secrets, links, branch, sync, task board, lint, tests, locks, commits). `--quiet` suppresses status outputs.
- `./helper.sh issue <create|list|checkout|close|sync>`: Subtask and issue lifecycle tracking.
- `./helper.sh lock [<module> | --release <module> | --clear-all | --prune]`: Acquires module locks. Use `--clear-all` to clear all locks, and `--prune` to remove stale locks.
- `./helper.sh commit [-i | --interactive]`: Fires safe git commit command gated by validation guard. `-i` starts the interactive Conventional Commit helper.
- `./helper.sh profile <add|switch|list|apply>`: Credentials rotation and auto-sync config.
- `./helper.sh changelog`: Conventional commits parser and SemVer version bump.
- `./helper.sh sync`: Updates skills and ADR registries.
- `./helper.sh learn "<lesson>" [--category <name>]`: Appends a lesson to `.agents/memory/lessons-learned.yaml`.
- `./helper.sh token [<log | status | sync | reset>]`: Logs/displays token budget statistics. Defaults to status if subcommand is omitted.
- `./helper.sh heartbeat`: Runs workspace heartbeat diagnostic checks.
- `./helper.sh pause`: Halts agent execution (blocks any tool/command runs by the agent).
- `./helper.sh resume`: Reactivates agent execution after being paused.
- `./helper.sh doctor`: Diagnostics tool verifying local setup and python dependencies.
- `./helper.sh mcp <register|start>`: Model Context Protocol integration. Supports local/global registration and server execution.

## 2. Context map — what loads when

| Path | Contents | When it loads |
|---|---|---|
| `AGENTS.md` | Identity, non-negotiables | Always — every prompt |
| `.agents/rules.md` | Project-specific stack, style, and testing rules (language, lint, frameworks) | Always — loaded alongside `AGENTS.md` every prompt |
| `.agents/skills/adr/SKILL.md` | Standardized playbook and template for generating new Architectural Decision Records. | On match |
| `.agents/skills/code-review/SKILL.md` | Guidelines and checklists for performing high-quality, zero-regression code reviews. | On match |
| `.agents/skills/contract-synchronization/SKILL.md` | Playbook for managing API contract schemas, generating client code, and verifying backend/frontend synchronization. | On match |
| `.agents/skills/database-evolution/SKILL.md` | Playbook for writing safe database migrations, managing schema evolutions, executing reversible rollbacks, and avoiding table lock contention in enterprise environments. | On match |
| `.agents/skills/devops-release/SKILL.md` | Playbook for setting up CI/CD pipelines, automating linting, testing, building, caching, and staging release gates. Guidelines for containerization (Dockerfile best practices), release versioning, blue-green deployment, feature flag rollouts, and post-deployment smoke verification. | On match |
| `.agents/skills/documentation/SKILL.md` | API docstrings, onboarding manuals, blueprints, and docs sync playbook | On match |
| `.agents/skills/engineering-standards/SKILL.md` | Principles, workflows, and standards for writing clean, secure, and highly optimized code, including guidelines for code writing, code review, and architectural integrity. SOLID refactoring, guard clauses, TDD, and legacy migration playbook Guidelines for CPU profiling, identifying database query bottlenecks (N+1 queries), diagnosing memory leaks, and optimizing resource execution speeds. | On match |
| `.agents/skills/mcp-execution/SKILL.md` | "Guidelines and strict anti-hallucination protocols for safely executing lazy-loaded MCP tools without guessing JSON schemas." | On match |
| `.agents/skills/observability/SKILL.md` | Guidelines for implementing structured logging, distributed tracing (OpenTelemetry), performance metrics, and centralized error telemetry. | On match |
| `.agents/skills/security-compliance/SKILL.md` | Diagnostic playbook for scanning vulnerabilities, verifying secret exclusion, and executing OWASP Top 10 compliance audits. Package pinning, license auditing, upgrade verification, and package pruning playbook. | On match |
| `.agents/skills/skill-evolution/SKILL.md` | Playbook instructing agents how to dynamically formulate, design, bootstrap, and register new workspace skills when facing skill gaps. | On match |
| `.agents/skills/swarm-orchestration/SKILL.md` | Playbook for delegating tasks to subagents, utilizing isolated branch workspaces to prevent code conflicts, and aggregating pull requests. | On match |
| `.agents/skills/testing/SKILL.md` | Playbook for executing unit and integration tests, mocking external services, and structuring test suites. | On match |
| `.agents/skills/troubleshooting/SKILL.md` | Diagnostic playbook for troubleshooting CLI errors, shell script crashes, and test failures. Diagnostic and recovery playbook for resolving local git states, locked configuration files, broken workspace setups, and process deadlocks. | On match |
| `.agents/skills/ui-ux-design/SKILL.md` | Strict guidelines enforcing modern UI aesthetics (Glassmorphism, Dark-mode first), micro-animations, Accessibility (a11y), and Core Web Vitals optimization. | On match |
| `.agents/workflows/*.md` | Slash-command macros (e.g. `/sync-memory`) | Only when the command is run |
| `.agents/memory/architecture.md` | Compressed system summary | Pulled on demand (`@.agents/memory/architecture.md`) before architecture-affecting work |
| `.agents/memory/decisions/` | ADRs — full reasoning | On demand |
| `.agents/memory/glossary.md` | Domain terms | On demand when unfamiliar terms appear |
| `.agents/memory/tech-debt.md`, `lessons-learned.yaml` | Known shortcuts, past incidents | On demand before related work; appended after the fact |
| `.agents/memory/milestones.md` | Release milestones and roadmap tracker | On demand, read when scoping upcoming versions or cross-feature milestones |
| `.agents/memory/security-policy.md` | Security runbook and network safelist | On demand, read when performing security audits or changing credentials/profiles |
| `.agents/docs/collaboration.md` | Agent-Human collaboration protocol | On demand, read when resolving workspace/lock conflicts or coordinating tasks |
| `.agents/blueprints/` | Reference architectural blueprints (Clean/Hexagonal, DDD, MVC, Monorepo, Atomic Component Design) | On demand, read when planning layout structures or component hierarchies |
| `.agents/soul.md` | Core agent values, communication policies, and identity. | Always — loaded alongside `AGENTS.md` every prompt |
| `.agents/tasks/board.md` | Task board | Read at the start of every task, written at every status change |
| `.agents/config.json` | Advanced workspace-level runtime and workflow settings (e.g. solo mode) | Read dynamically during commands/validations |
| `.agents/git_profiles.json` | Developer Git profiles, author emails, signing keys, and push credentials | Applied dynamically when switching profiles or committing |
| `.agents/projects.json` | Monorepo component paths, stacks, local test commands, and contract schemas | Audited dynamically during monorepo validations |
