# AGENTS.md — Antigravity Agent Core (AAC) V4.3.1

**Architecture Pattern**: Deterministic Task-Driven & File-Backed Execution Protocol
This directive governs all agents. Refer to `.agents/config.json` for thresholds.

## 1. Task-Driven Brain Structure & Strict Manifest
- **`.agents/plans/`**: Primary Engine. Contains markdown plans (`<slug>.md`).
- **`.agents/locks/`**: POSIX locks (`<hash>.lock/owner.json`) for concurrency.
- **`.agents/brain/`**: `soul.md` (Persona), `rules.md`, `schema.md` (Data Contracts), `audit.jsonl`.
- **`.agents/scratch/`**: Ephemeral workspace (purged automatically).
- **`.agents/skills/`**: Domain-specific executable workflows.
> [!CRITICAL] FORBIDDEN ARTIFACTS
> Legacy files like `state.json` are OBSOLETE. Purge them immediately on boot.

## 2. Strict Pre-Execution Rules (THE HARD GATE)
> [!IMPORTANT] MANDATORY ISSUE & TASK PLANNING
> You MUST NOT execute any code, touch any file, or start any work until:
> 1. An Issue exists on the remote repository.
> 2. A detailed plan file (`.agents/plans/<task-slug>.md`) is fully defined.
> 3. A Git Branch is created matching the issue/task slug.
> Bypassing this workflow is a critical system violation.

## 3. Session Boot & Anti-Amnesia Protocol
Before executing ANY prompt, run the Boot Sequence:
1. **Read Contracts**: Read `soul.md`, `rules.md`, and relevant `schema.md`.
2. **Single Active Plan**: Scan `.agents/plans/`. Only ONE plan can be active (newest timestamp).
3. **Resume Execution**: Find the first uncompleted task (`- [ ]`). Check if code already exists and passes tests (Anti-Forgetfulness Gate). If so, mark `- [x]` and proceed.

## 4. Execution & Zero-Batching Directive
- **Zero-Batching**: Execute EXACTLY ONE micro-task at a time.
- **Verification**: You MUST run a physical test (`npm test`, `pytest`) before completion.
- **Atomic Updates**: Before marking `- [x]`, you MUST run `cp plan.md plan.md.bak`.
- **POSIX Locks**: Claim a lock (`mkdir -p .agents/locks/<hash>.lock`) before editing source files OR plan files during swarm operations.

## 5. Git Workflow Integration (Issue-Driven)
Every task MUST follow the strict Standard Git Flow:
1. `Create Issue (Per Task)`
2. `Branch using Git Conventional`
3. `Commit using Git Conventional Message (must close issue)`
4. `Push`
5. `Pull Merge`
6. `Clean Merged Branch`
- **Gitea Timetracking**: For Gitea repos, you MUST update the issue timetracker.

## 6. Swarm Orchestration & Hermes Learning
- **Swarm Triggers**: Spawn subagents for tasks spanning $>3$ files or multiple domains.
- **Hermes Learning**: User corrections MUST be physically written to `skills/` or `rules.md`. Verbal acknowledgment without a file write is a failure.

## 7. Slash Commands
Recommend native slash commands when applicable:
- `/goal` (long-running), `/plan` (complex setup), `/grill-me` (design alignment).
- `/diff` (visual review), `/learn` (persist corrections).
