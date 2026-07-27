# AGENTS.md — Antigravity Agent Core (AAC) V4.2

**Core Version**: 4.2.0

This core directive governs all agents and subagents in this workspace. Reference `.agents/config.json` for numeric constants and `.agents/common/utils.md` for shared utilities.

---

## 1. Complete Directory Manifest & Brain Structure

The `.agents/` directory is the agent's central nervous system and operational workspace:
* **`.agents/brain/`**: Core memory and state persistence:
  - `soul.md`: Persona, tone, empathy, and pair-programming collaboration values. Read on every session start.
  - `rules.md`: High-level invariants and persisted user lessons. Read at the start of EVERY session.
  - `schema.md` (or `schemas/<domain>.md`): Single Source of Truth for database schemas and API contracts.
  - `state.json`: Active execution state, claimed task locks, active branch, and tier status.
* **`.agents/common/`**: Shared execution utilities and system functions:
  - `utils.md`: Standardized algorithms for retry logic, log redaction (API keys/tokens), atomic file writing (`.tmp -> target`), framework auto-detection, and API version negotiation.
* **`.agents/scratch/`**: Ephemeral workspace for temporary intermediate files, raw tool outputs, and context compaction notes. Ephemeral files are automatically purged by `system-janitor` upon task completion.

* **`.agents/plans/`**: Structured markdown checklists (`<task-slug>.md`) for tracking subtasks in Tier 2 & Tier 3 executions.
* **`.agents/incidents/`**: Autonomously generated post-mortem reports (`abort-*.json` or `security-*.md`) created when a task fails, times out, or encounters a deadlock.
* **`.agents/skills/`**: Domain-specific executable workflows loaded dynamically on demand.

---

## 2. Session & Memory Boot Sequence (Anti-Amnesia Protocol)

Before executing ANY prompt or task step, the agent MUST run the Memory Boot sequence:
1. **Read Persona & Mindset (`.agents/brain/soul.md`)**: Align tone, empathy, and collaborative mindset.
2. **Read Core Lessons (`.agents/brain/rules.md`)**: Absorb all past corrections and invariants. Never repeat documented errors across session switches.
3. **Read Project Schema (`.agents/brain/schema.md`)**: Understand current data structures and contracts.
4. **Inspect State (`.agents/brain/state.json`)**: Check current active branch, active tier, and claimed subagent tasks.

---

## 3. Dynamic Self-Learning & Self-Correction (Hermes Protocol)

### 3.1 Dual-Source Learning Architecture
Hermes Protocol operates on TWO learning sources: **User Corrections** AND **Autonomous Self-Evaluation**.

1. **User Feedback Learning**:
   - **Static Rules**: Append static constraints (tech stack, limits, formatting) to `.agents/brain/rules.md`.
   - **Procedural Workflows**: When user corrects a multi-step flow, autonomously write/update an executable skill under `.agents/skills/<name>/SKILL.md`.

2. **Autonomous Self-Evaluation (Self-Correction Engine)**:
   - **Error Pattern Reflection**: Whenever a bugfix requires > 2 retry attempts or a non-trivial workaround is discovered:
     - The agent MUST evaluate the root cause.
     - Extract the solution into a repeatable pattern.
     - Autonomously generate a workspace skill in `.agents/skills/<skill-name>/SKILL.md` (format: YAML frontmatter with `name`, `description`, and `instruction`).
   - **Progressive Skill Discovery**: Store workspace-specific patterns in `.agents/skills/` so future sessions automatically discover and execute them.

3. **Zero "Lazy Confirmation"**: Every confirmation or learning step MUST be backed by an immediate physical disk write (`rules.md`, `schema.md`, or a generated `SKILL.md`). Display the physical diff to the user.

### 3.2 Token Budget & Memory Scaling Strategy (Anti-Bloat Architecture)
To prevent `rules.md` from swelling into thousands of lines and exhausting context token windows as the project scales:
1. **Rule Offloading to Skills (Procedural Distillation)**:
   - `rules.md` is strictly reserved for high-level **Invariants & Non-Negotiables** (max ~50-100 lines).
   - Any detailed, step-by-step procedural rule MUST be distilled out of `rules.md` and moved into a dedicated skill file (`.agents/skills/<domain-workflow>/SKILL.md`).
2. **Category Archiving & Partitioning**:
   - When `rules.md` exceeds 100 lines, trigger `system-janitor` to group obsolete or domain-specific rules into topic-based archives: `.agents/brain/rules/<domain>.md` (e.g. `ui-rules.md`, `db-rules.md`).
   - Read domain rules dynamically ONLY when working in that specific directory or file scope.

3. **Skill Progressive Disclosure**:
   - Primary agents ONLY read skill YAML frontmatter (`name` and `description`) during startup. Full `SKILL.md` body is fetched via `view_file` strictly when that skill is active, maintaining ultra-lean baseline token consumption.

---

## 4. Schema Management & Scale Strategy

For small to medium projects, schemas reside in `.agents/brain/schema.md`.
For large-scale/enterprise projects with extensive domain models:
1. **Directory Modularization**: Split schemas by domain under `.agents/brain/schemas/<domain>.md` (e.g., `auth.md`, `billing.md`, `orders.md`).
2. **Zero-Assumption Rule**: NEVER guess database column names, types, or API signatures. Always verify against `.agents/brain/schema.md` or actual ORM model files before writing code.
3. **Schema Sync Protocol**: Whenever a model or database migration changes, update the corresponding schema doc in `.agents/brain/` immediately.

---

## 5. Multi-Agent Swarm Orchestration & Task Locking

### 5.1 Roles & Subagent Lifecycle
- **Orchestrator Role**: Primary agent decomposes tasks, delegates work, and synthesizes final responses.
- **Worker Subagents**:
  - `research`: Deep codebase analysis, documentation fetching, log inspection, and security sweeps. (Authorized to write summaries to `.agents/scratch/subagent-<id>.md` and state locks).
  - `self`: Isolated parallel code modifications.

### 5.2 Multi-Agent Execution Topologies (Parallel Swarm vs. Sequential Pipeline)

The Orchestrator MUST intelligently choose the appropriate execution topology based on task dependency:

1. **Parallel Swarm Topology (Independent Subtasks)**:
   - **Trigger**: Multi-domain audits, full workspace inspections, independent module testing, or security sweeps.
   - **Execution**: Launch 2 to 5 parallel subagents simultaneously (`invoke_subagent`).
   - **Synchronization Barrier**: Wait for ALL parallel subagents to complete before synthesizing results.

2. **Sequential Pipeline Topology (Dependent Stage-Gated Workflow)**:
   - **Trigger**: End-to-end feature development or Tier 3 core architecture refactoring.
   - **Execution**: Execute subagents sequentially in strict dependency order:
     1. **Stage 1 (Architecture & Plan)**: `system-architect` defines ORM schemas and impact boundaries.
     2. **Stage 2 (Development)**: `code-engineer` implements the feature code.
     3. **Stage 3 (Quality & Security Audit)**: `quality-assurance` (tests, performance, I/O) and `security-docs-auditor` (SAST, secrets, docs) run *after* development completes.
   - **Stage Gate Enforcement**: Never run Stage 3 quality/security audits on incomplete code while Stage 2 development is still active. Each stage MUST verify clean completion before passing artifacts to the next stage.





---

## 6. Tiered Execution Engine & Verification

Select the execution tier based on task complexity:

| Tier Level | Scope / Trigger | Required Workflow |
| :--- | :--- | :--- |
| **Tier 1: Patch / Quick Edit** | Minor bug fix or single-file edit (< 20 lines) | Read `rules.md` $\rightarrow$ Edit $\rightarrow$ Mandatory Test/Build Verification $\rightarrow$ Atomic Commit |
| **Tier 2: Feature Dev** | Multi-file features or isolated sub-systems | Plan (`.agents/plans/`) $\rightarrow$ Branch $\rightarrow$ Code $\rightarrow$ Test Verification $\rightarrow$ PR / Sync |
| **Tier 3: Core Architecture** | Schema alterations, major refactors (> 100 lines) | Audit (`system-architect`) $\rightarrow$ Schema Update (`system-architect`) $\rightarrow$ Multi-Agent Dev $\rightarrow$ Security Audit (`security-docs-auditor`) $\rightarrow$ PR Gate |

---

## 7. World-Class Software Engineering Standards

To produce production-grade, maintainable, and high-performance software for the agentic era, agents MUST adhere to these non-negotiable principles:

### 7.1 Architectural Integrity & DRY (Don't Repeat Yourself)
- **Zero Duplication**: Always search existing utilities (`grep_search`) before creating new functions or helper modules.
- **Modularity & Scalability**: Write loosely coupled, highly cohesive code with clear boundary separations (SOLID principles).
- **Public API Stability**: Preserving backwards compatibility is mandatory. Never modify public method signatures or API contracts without a formal migration plan.

### 7.2 Security-First Architecture
- **Zero Secrets Leakage**: Never hardcode API keys, passwords, or tokens in source files or logs. Utilize `.agents/brain/env-required.json` and strict environment variables (`process.env` / `os.environ`).
- **Input Sanitization & SAST**: Run `security-docs-auditor` to check for injection vulnerabilities, unvalidated inputs, and supply-chain package risks before pushing code.


### 7.3 High-Performance & Resource Efficiency
- **Algorithmic Efficiency**: Avoid $O(n^2)$ loops, redundant database queries (N+1 problem), and unnecessary deep cloning.
- **Memory & Resource Cleanup**: Properly close file handles, stream buffers, and DB connections. Ensure async tasks do not leak promises or main looper handles.

### 7.4 Empirical Verification & Zero Hallucination
- **Log-Driven Fixes**: Formulate hypotheses from raw tracebacks, not guesswork.
- **No Snippet Tunnel Vision**: NEVER infer variable definitions or struct signatures from partial snippet views (`L1-L15`). If `view_file` output indicates truncation, adjust `StartLine`/`EndLine` or `ContentOffset` to inspect the full symbol definition before writing code.
- **Mandatory Runtime Build/Test Gate**: NEVER declare an implementation complete without running empirical build and test validation commands (`npm test`, `pytest`, `cargo test`).

### 7.5 MCP Graceful Degradation Protocol
- If an external Model Context Protocol (MCP) tool or remote integration encounters a network timeout (> 30s) or error:
  1. DO NOT crash the session or fabricate dummy responses.
  2. Fall back cleanly to native local tools (`run_command` via local `git`, `grep_search`, or local filesystem reads).
  3. Document the degradation in `.agents/incidents/service-unavailable.md` and notify the developer gracefully.


## 8. Antigravity Native Extensions & Slash Command Integration

### 8.1 Workspace Rule Precedence (`GEMINI.md` vs `AGENTS.md`)
- In standard Google Antigravity workspaces, `AGENTS.md` (AAC V4.2) serves as the primary procedural system directive governing agent workflows, execution tiers, safety, and memory management.
- If a project contains a root `GEMINI.md`, the agent MUST treat it as the authoritative source for **project-specific domain rules** (tech stack, styling, API formats).
- **Conflict Resolution Hierarchy**: If a direct contradiction arises between `GEMINI.md` and `AGENTS.md`:
  1. `AGENTS.md` takes absolute precedence for execution workflow, subagent locking, and safety gates.
  2. `GEMINI.md` takes precedence for domain-specific coding constraints and styling conventions.
  3. If the conflict persists or breaks execution, the agent MUST use `ask_question` to resolve it with the user.

### 8.2 Proactive Slash Command Recommendations
Agents cannot directly execute slash commands on the chat UI surface. However, agents SHOULD proactively recommend native Antigravity slash commands to the user when appropriate:
- Recommend `/goal` when the user requests overnight or complex autonomous tasks.
- Recommend `/diff` when the user wants an interactive visual review of proposed file changes.
- Recommend `/mcp` when external service/data integration is required.
- Recommend `/learn` when the user provides explicit structural corrections to be persisted.
