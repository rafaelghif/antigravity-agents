# AGENTS.md — Antigravity Agent Core (AAC) V4.3.1

**Architecture Pattern**: Deterministic Task-Driven & File-Backed Execution Protocol
This directive governs all agents. Reference `.agents/config.json` for numerical thresholds.

---
## 1. Directory Manifest (Strict Adherence)
* **`.agents/plans/`**: Primary Execution Engine. Active markdown checklists (`<slug>.md`).
* **`.agents/locks/`**: POSIX locks (`<hash>.lock/owner.json`) for TOCTOU prevention.
* **`.agents/brain/`**: `soul.md` (Persona), `rules.md`, `schema.md` (Data Contracts), `audit.jsonl`.
* **`.agents/scratch/`**: Ephemeral workspace (purged automatically).
* **`.agents/skills/`**: Domain-specific executable workflows.

> [!CRITICAL] FORBIDDEN ARTIFACTS
> Legacy state files (e.g. `state.json`) are OBSOLETE and FORBIDDEN. Purge immediately on boot.

---
## 2. THE HARD GATE (Strict Pre-Execution Workflow)
> [!IMPORTANT] ISSUE & TASK PLANNING ARE MANDATORY
> You MUST NOT execute code, touch source files, or start work until:
> 1. An **Issue** exists on the remote repository (GitHub/Gitea). You MUST empirically verify or create the issue using the strict Priority Fallback: 1) MCP, 2) CLI, 3) Human Report. NEVER guess or hallucinate issue IDs.
> 2. A detailed plan file (`.agents/plans/<task-slug>.md`) is fully defined.
> 3. A Git Branch is created matching the issue (e.g. `task/issue-123-<slug>`).
> Bypassing this workflow is a CRITICAL SYSTEM VIOLATION.

---
## 3. Session Boot & Task Recovery Protocol
Before executing ANY prompt, run the Boot Sequence:
1. **Read Contracts**: Read `soul.md`, `rules.md`, and relevant `schema.md`.
2. **Scan Active Plans**: Check `.agents/plans/*.md`. Only ONE plan can be active (newest timestamp).
3. **Resume Execution**: Find the first uncompleted task (`- [ ]`). 
   * **Plan Re-Validation Protocol**: If resuming a paused plan, validate that the remaining tasks still align with the current codebase architecture. Do not execute blindly.
   * **Anti-Forgetfulness Gate**: If code for `- [ ]` already exists and passes empirical verification (`npm test`), mark `- [x]` and proceed.

---
## 4. Execution & Zero-Batching Directive
- **Zero-Batching**: Execute EXACTLY ONE micro-task at a time.
- **Empirical Verification Gate**: You CANNOT mark `- [x]` based on confidence. You MUST have physical terminal output (`exit code 0` from `npm test` or `tsc`).
- **Atomic Backup**: Run `cp plan.md plan.md.bak` BEFORE marking `- [x]`.
- **POSIX Locks**: Claim a lock (`mkdir -p .agents/locks/<hash>.lock`) before modifying source files or plans during swarm operations. Locks expire after 60s.

---
## 5. Standard Issue-Driven Professional Git Workflow
Every task MUST follow this exact strict sequence:
1. `Create Issue` (Per Task) - You MUST follow the **Platform Interaction Priority Fallback**:
   - **Priority 1**: Use MCP Server APIs (primary native method).
   - **Priority 2**: Use CLI (`gh` / `git`) if MCP is unavailable.
   - **Priority 3**: HARD STOP and explicitly report to the Human to check if both fail. Zero guessing allowed.
   *Issue titles MUST use Git Conventional format (e.g., `feat: ...`, `fix: ...`). Issue bodies MUST be detailed and professional.*
2. `Branch using Git Conventional` (e.g., `fix/issue-95-slug`).
3. `Commit using Git Conventional Message` (MUST close issue).
4. `Push`
5. `Create PR` - Direct merges to main are FORBIDDEN. Create a Pull Request via CLI (`gh pr create`).
6. `Merge PR` - Use `gh pr merge`.
7. `Update Release & Changelog` - Every merged PR must be accompanied by a version bump and CHANGELOG entry.
8. `Clean Merged Branch`
- **Gitea Timetracking**: For Gitea repositories, you MUST update the issue timetracker.

---
## 6. Tiered Execution Engine
| Tier | Scope | Workflow |
| :--- | :--- | :--- |
| **T1: Patch** | < 50 lines | Read `rules.md` -> Edit -> Verify -> Atomic Commit |
| **T2: Feature** | >= 50 lines | Plan in `.agents/plans/` -> Branch -> Micro-Tasks -> Verify -> Merge |
| **T3: Architect** | Refactor | Audit -> Schema Update -> Plan -> Swarm Dev -> Security Audit -> Merge |

---
## 7. Swarm Orchestration & Hermes Learning
- **Swarm Triggers**: Spawn subagents for tasks spanning >= 3 files or multiple domains.
- **Hermes Learning (Dual-Source)**: User corrections MUST be physically written to `skills/` or `rules.md`. Verbal acknowledgment without a physical disk write is a failure.

---
## 8. Slash Commands
Recommend native slash commands when applicable:
- `/goal` (long-running autonomous execution)
- `/plan` (complex setup)
- `/grill-me` (design alignment interview)
- `/diff` (interactive visual review)
- `/learn` (persist user corrections)
