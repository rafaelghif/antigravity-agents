# AGENTS.md — Antigravity Agent Core (AAC) V4.3

**Core Version**: 4.3.0  
**Architecture Pattern**: Deterministic Task-Driven & File-Backed Execution Protocol

This core directive governs all agents and subagents in this workspace. Reference `.agents/config.json` for numeric constants and `.agents/common/utils.md` for shared utilities.

---

## 1. Complete Directory Manifest & Task-Driven Brain Structure

The `.agents/` directory is the agent's central nervous system and operational workspace:
* **`.agents/plans/`**: **Primary Execution Engine (Single Source of Truth)**. Contains active, granular markdown plan checklists (`<task-slug>.md`). Every non-trivial task MUST have a plan file here before code execution begins.
* **`.agents/locks/`**: **POSIX Directory-Based Mutex Locks**. Contains atomic lock directories (`.agents/locks/<md5_hash_of_filepath>.lock/`) to prevent TOCTOU race conditions across parallel subagents.
* **`.agents/brain/`**: Core memory & contract specifications:
  - `soul.md`: Persona, tone, empathy, and pair-programming collaboration values. Read on every session start.
  - `rules.md`: High-level invariants and persisted user lessons. Read at the start of EVERY session.
  - `schema.md` (or `schemas/<domain>.md`): Single Source of Truth for database schemas, table column definitions, and API contracts.
  - `audit.jsonl`: Immutable task execution and token consumption audit trail.
  - `env-required.json`: Declaration of required environment variables and secrets.
  - `mcp-registry.json`: Registry of dynamic Model Context Protocol (MCP) server endpoints.
* **`.agents/common/`**: Shared execution utilities and system functions (`utils.md`).
* **`.agents/scratch/`**: Ephemeral workspace for temporary intermediate files. Ephemeral files are automatically purged by `system-janitor` upon task completion.
* **`.agents/incidents/`**: Autonomously generated post-mortem reports (`abort-*.json` or `security-*.md`).
* **`.agents/skills/`**: Domain-specific executable workflows loaded dynamically on demand.

> [!CRITICAL] STRICT DIRECTORY MANIFEST INVARIANT
> Any file or state artifact NOT explicitly listed in this manifest (such as legacy `state.json`) is strictly classified as OBSOLETE/DEPRECATED and FORBIDDEN to exist. If detected during Session Boot, the agent MUST purge it immediately.


---

## 2. Session Boot & Anti-Amnesia Protocol (Task-Driven Recovery)

Before executing ANY prompt or task step, the agent MUST run the Memory & Task Recovery Boot sequence:

1. **Read Persona & Invariants**:
   - Read `.agents/brain/soul.md` (Persona & Empathy).
   - Read `.agents/brain/rules.md` (Invariants & Lessons).
2. **Inspect Active Task Registry & Storage Cleanup (Direct Filesystem Scan)**:
   - Perform a direct filesystem scan of the `.agents/plans/` directory for any active `<task-slug>.md` plan files containing uncompleted checkboxes (`- [ ]` or `- [~]`).
   - If a plan file is malformed or corrupted due to a past system crash, immediately restore from `.agents/plans/<task-slug>.md.bak`.
   - **Orphan Scratch Cleanup**: Autonomously purge any ephemeral files in `.agents/scratch/` that do not belong to active task plans to prevent context confusion across session switches.
3. **Session & Interrupt Recovery Protocol (ZERO Amnesia & Anti-Redundancy Gate)**:
   - If an active plan exists with uncompleted tasks (`- [ ]` or `- [~]`):
     - **DO NOT ask the user what to do next**.
     - **DO NOT start over or re-implement finished tasks (`- [x]`)**.
     - If a task is marked `- [~] (Assigned: <subagent_id>)`, check if the subagent is still active before re-delegating or executing.
     - Identify the **FIRST uncompleted micro-task** (`- [ ]`) in the plan.
     - **Empirical Artifact Pre-Check (Anti-Forgetfulness Gate)**: Before executing code for `- [ ]`, inspect if the target file/function exists AND passes empirical verification (`npm test`, `tsc`, `pytest`). DO NOT rely on simple file presence alone. If the code exists AND passes verification, update the checkbox to `- [x]` and proceed to the next micro-task. If verification fails, repair the existing code.
     - Inspect its explicit references (e.g. `Ref: schema.md#table_name`, `Target File: src/...`) and resume execution.

4. **Read Domain Contracts**: Read `.agents/brain/schema.md` (or relevant `schemas/<domain>.md`) referenced by the active micro-task.

---

## 3. Engineering-Grade Task Definition Protocol (Spec-First Architecture)

### 3.1 Strict Pre-Execution Rules (Hard-Lock Gate)
- **No Code Without a Task Plan**: No source code file may be created or edited (Tier 2/Tier 3) until a detailed plan file `.agents/plans/<task-slug>.md` has been written and persisted to disk.
- **Workflow Bypass Prohibition**: Writing code before completing (1) Plan File Creation and (2) Git Branch Creation (`git checkout -b task/<task-slug>`) is strictly classified as a **System Violation**.
- **Micro-Task Granularity Standard**: Tasks in `.agents/plans/` CANNOT be high-level vague statements like "Create User CRUD". They MUST be broken down into micro-units of execution.

### 3.2 Granular Micro-Task Plan Format & Zero-Batching Directive
> [!CRITICAL] ZERO-BATCHING DIRECTIVE
> You are FORBIDDEN from executing multiple uncompleted micro-tasks (`- [ ]`) in a single step.
> 1. Execute EXACTLY ONE micro-task.
> 2. Run the empirical validation command (`npm test`, `tsc`, `pytest`).
> 3. Update the plan file to `- [x]` using `replace_file_content`.
> 4. STOP and proceed to the next micro-task sequentially.

Every `.agents/plans/<task-slug>.md` file MUST strictly follow the structure defined in `.agents/TASK_TEMPLATE.md` (including `## 1. Decisions & Architectural Trade-offs`, DTOs, Repository, Controllers, and Verification Gates).


---

## 4. Atomic Progress Checkpointing & Interrupt Safety

To guarantee zero loss of context during network disconnects, session switches, token compaction, or user interrupts:

1. **Atomic Checkpointing After EVERY Micro-Task**:
   - As soon as a single micro-task is complete and verified, the agent MUST immediately edit `.agents/plans/<task-slug>.md` using `replace_file_content` to mark it as `- [x]`. Always create a `.bak` backup before editing.
2. **Crash & Interrupt Recovery State**:
   - On the next prompt or session reload, the agent inspects the file directly, sees `- [x]` for finished items, and picks up at the very first `- [ ]` item.
3. **Zero Amnesia Merging**: When multiple micro-tasks are completed, the progress log in the plan file serves as the definitive audit trail.

---

## 5. Dynamic Self-Learning & Self-Correction (Hermes Protocol)

### 5.1 Dual-Source Learning Architecture
Hermes Protocol operates on TWO learning sources: **User Corrections** AND **Autonomous Self-Evaluation**.

1. **User Feedback Learning (Physical Activation Requirement)**:
   - **Mandatory Disk Write**: When a user corrects a workflow, structural error, or provides an explicit new constraint, the agent MUST physically write/update an executable skill under `.agents/skills/<skill-slug>/SKILL.md` (or append to `rules.md`). **Mere verbal chat acknowledgment is considered a system failure.**
2. **Autonomous Self-Evaluation (Self-Correction Engine)**:
   - Whenever a bugfix requires > 2 retry attempts, extract the solution into a repeatable pattern and generate a workspace skill physically under `.agents/skills/`.
3. **Zero "Lazy Confirmation"**: Every confirmation or learning step MUST be backed by an immediate physical disk write. Display the physical diff to the user.

---

## 6. Multi-Agent Swarm Orchestration & POSIX Task Locking

### 6.1 Roles & Mandatory Swarm Triggers
- **Orchestrator Role**: Primary agent decomposes tasks into `.agents/plans/`, delegates work, and synthesizes final responses.
- **Mandatory Swarm Triggers**: The Orchestrator MUST autonomously split execution into a Multi-Agent Swarm (`invoke_subagent`) if any of the following conditions are met:
  1. **Multi-File Audits**: The task requires auditing, reading, or analyzing $\ge 3$ files.
  2. **Multi-Domain Tasks**: The task spans multiple functional domains (e.g., UI Components + Backend API + DB Schema).
  3. **High Complexity**: The execution token budget is predicted to be exceeded by a single agent.
- **Worker Subagents**:
  - `research`: Deep codebase analysis, document fetching, and summary aggregation.
  - `self`: Isolated parallel code modifications bound strictly to an assigned micro-task block.

### 6.2 POSIX Directory-Based File Locking Protocol
- **File Lock Claiming**: Any subagent attempting to modify a specific file path MUST claim an explicit atomic directory lock (`mkdir -p .agents/locks/<md5_hash_of_filepath>.lock`) containing `owner.json` metadata (`{"claimed_by": "<agent_id>", "claimed_at": "<ISO8601>"}`).
- **Lock Timeout**: Locks auto-expire after `config.json -> state_management.lock_timeout_seconds` (60s) to prevent orphan deadlocks.

---

## 7. Tiered Execution Engine & Mandatory Verification

Select the execution tier based on task complexity:

| Tier Level | Scope / Trigger | Required Workflow |
| :--- | :--- | :--- |
| **Tier 1: Patch / Quick Edit** | Minor bug fix or single-file edit (< 50 lines) | Read `rules.md` $\rightarrow$ Edit $\rightarrow$ Mandatory Test/Build Verification $\rightarrow$ Atomic Commit |
| **Tier 2: Feature Dev** | Multi-file features or single-file edits ($\ge 50$ lines) | Define Granular Plan in `.agents/plans/` $\rightarrow$ Branch Isolation $\rightarrow$ Atomic Micro-Task Execution $\rightarrow$ Test Verification $\rightarrow$ Sync |
| **Tier 3: Core Architecture** | Schema alterations, major refactors (> 100 lines) | Audit (`system-architect`) $\rightarrow$ Schema Update (`schema.md`) $\rightarrow$ Plan in `.agents/plans/` $\rightarrow$ Multi-Agent Swarm Dev $\rightarrow$ Security Audit $\rightarrow$ Gate |

### 7.1 Mandatory Runtime Build/Test Gate & Zero-Assumption Verification
> [!IMPORTANT] ZERO-ASSUMPTION VERIFICATION
> You CANNOT mark a micro-task as `- [x]` based on confidence or subjective belief.
> Evidence Requirement: You MUST have physical terminal output showing `exit code 0` in your context window. If you haven't run the build/test command, YOU DO NOT KNOW if it works.


---

## 8. Git Workflow Integration & Workspace Isolation

### 8.1 Branching per Task Plan
- **Task Isolation**: Before executing code modifications for Tier 2 or Tier 3 tasks, the agent MUST automatically integrate with Git by creating a dedicated branch or worktree matching the task slug (e.g., `git checkout -b task/<task-slug>`).
- **Atomic Commits**: Code modifications MUST be committed atomically matching the completion of micro-task phases in the active plan.

---

## 9. Antigravity Native Extensions & Slash Command Integration

### 9.1 Proactive Slash Command Recommendations
Agents SHOULD proactively recommend native Antigravity slash commands to the user when appropriate:
- Recommend `/goal` when the user requests overnight or complex autonomous tasks.
- Recommend `/plan` when initializing complex multi-step features.
- Recommend `/grill-me` when design decisions or architectural trade-offs require alignment.
- Recommend `/diff` when the user wants an interactive visual review of proposed file changes.
- Recommend `/learn` when the user provides explicit structural corrections to be persisted.


