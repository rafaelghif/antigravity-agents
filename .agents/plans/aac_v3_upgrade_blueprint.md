# Architectural Blueprint: Antigravity Agent Core (AAC) V3 Upgrade

This document outlines the proposed architectural changes, key enhancements, and implementation roadmap to transition the **Antigravity Agent Core (AAC)** from **V2** to **V3**. The focus of V3 is **Performance, Parallelization, Active Skill Execution, Multi-Agent Swarms, Isolated Sandboxing, and Proactive Token Guardrails**.

---

## 1. Executive Summary & Design Goals
The current AAC V2 architecture is highly stable, modular, and robust. However, as the repository scale and agent complexity grow, several bottlenecks emerge:
1. **Sequential Audits:** The validation guard runs all audits sequentially, increasing wait times during commit and check-in loops.
2. **Passive Skills:** Skills are restricted to markdown playbooks (`SKILL.md`) that the agent must read and interpret manually.
3. **Passive Token Auditing:** Token consumption is logged after the fact, but not actively enforced at runtime.
4. **Single-Agent Handoffs:** Subagents inherit contexts but lack concurrent communication or dynamic swarm orchestration.

### AAC V3 Core Design Objectives
* **Sub-Second Validation Overhead:** Parallelize and increment validation audits using Git status diff isolation.
* **Active Execution Skills:** Enable skills to register executable test suites, compilation rules, or pre-commit hooks.
* **Proactive Budgeting:** Introduce runtime token allocation and automatic process termination on budget overrun.
* **Multi-Agent Swarm (Asynchronous Handoffs):** Standardize peer-to-peer agent messaging systems to run specialized agents (Security, Reviewer, Coder) concurrently.
* **Zero-Poll Isolated Sandboxing:** Run code execution and validation audits inside secure, throwaway containers (e.g. lightweight Docker or virtual environments) to prevent filesystem contamination.

---

## 2. Proposed Architecture Upgrades

```mermaid
graph TD
    subgraph AAC V2 (Current)
        A[./helper.sh CLI Wrapper] --> B[validate.py - Sequential]
        A --> C[skill.py - Static markdown list]
        A --> D[token.py - Post-facto logs]
    end
    subgraph AAC V3 (Proposed)
        E[./helper.sh CLI Wrapper] --> F[Validate.py - Parallel / Asyncio Hooks]
        E --> G[Skill Engine - Active validation scripts & templates]
        E --> H[Token Budget Guard - Active runtime token limits]
        E --> I[Swarm Orchestrator - Asynchronous peer channels]
        E --> J[Sandbox Manager - Isolated container runner]
        F --> K[Incremental Git diff scanning]
    end
```

### A. Parallel Validation Engine (validate.py Upgrade)
* **Current Model:** Audits run sequentially (Critical Files -> Secrets -> Links -> Git Branch -> ...).
* **V3 Model:** Leverage Python `asyncio` or `concurrent.futures` to execute checks in parallel. 
* **Incremental Scans:** Audit only the files returned by `git diff --name-only` for link integrity, secrets scanning, and lints. Baseline checks (like branch naming or board schemas) run as global parallel hooks.
* **Expected Result:** Validation overhead reduced by up to **75%** on large developer trees.

### B. Active Skill Execution Framework
Currently, skills under `.agents/skills/` are documentation-only. In V3, a skill can include code definitions:
* **Directory Structure:**
  ```
  .agents/skills/<skill-name>/
    ├── SKILL.md          # Markdown playbook
    ├── schema.json       # CLI arguments schema definition
    ├── validate.py       # Custom pre-commit/validation script for this skill
    └── setup.sh          # Auto-installer for skill dependencies
  ```
* **Dynamic Loading:** The validation guard automatically scans and runs `validate.py` for all installed custom skills, allowing teams to add domain-specific syntax compilation rules dynamically without editing the core `validate.py` file.

### C. Active Token Budget & Cost Containment
* **Current Model:** Token usage logs are recorded in `token_usage.jsonl`.
* **V3 Model:** Define a `token_budget.json` config in the workspace specifying soft/hard limits per conversation session, day, or billing period.
* **Runtime Guard:** The CLI wraps model/platform API calls. Before sending prompts, it calculates the rolling usage; if the hard limit is breached, the execution is suspended, preventing accidental billing loops.

### D. Multi-Agent Swarm Orchestration
* **V3 Handoff Specification:** Implement an asynchronous agent-to-agent message broker (using simple file-based mailboxes under `.agents/messages/` or local sockets).
* **Specialized Agent Roles:**
  * **Architect:** Translates requests into ADR drafts and checks module boundary imports.
  * **Coder:** Dynamically scaffolds the source files on a feature branch.
  * **Reviewer:** Automatically reviews changes line-by-line using git diffs.
  * **Security Guard:** Scans dependencies and checks for OWASP vulnerabilities.
* **Benefit:** Eliminates single-agent fatigue and context window bloat by isolating roles to dedicated subagent contexts.

### E. Context-Insulated Sandboxing (Sandbox Manager)
* **V3 Isolation:** Prohibit tests and compilers from running directly on the host machine filesystem by default.
* **Docker/Venv Runners:** Scaffold a scratch directory or run a lightweight container to build code, run unit tests, and perform static syntax checks. This guarantees zero side-effects on developer systems and prevents untrusted script executions from leaking credentials.

---

## 3. Impact Analysis & Comparison

| Vector | Option A: Incremental V2 Extensions | Option B: Re-architect to V3 Core |
|---|---|---|
| **Performance** | Minor improvements; serial execution remains a bottleneck. | High; asyncio parallel execution achieves sub-second checks. |
| **Maintainability** | Lower risk; maintains backward compatibility. | Requires migration of validate and cli runner namespaces. |
| **Capability** | Skills remain passive documentation logs. | Skills become active agents of code quality and verification. |
| **Swarm Orchestration** | Flat single-agent delegation only. | Asynchronous concurrent multi-agent cooperation. |
| **Security & Safety** | Code execution runs directly on the host system. | Code runs in throwaway sandboxes, shielding host credentials. |

---

## 4. Implementation Roadmap & Phases

### Phase 1: Core CLI Parallelization & Sandbox Integration
1. Refactor `validate.py` to use `asyncio` for non-blocking IO file checks.
2. Build the `Sandbox Manager` to pipe validation commands into clean Docker containers.

### Phase 2: Active Skill Contracts & Swarm Handoffs
1. Update `sync.py` to index skill validation hooks.
2. Develop the `.agents/messages/` peer messaging protocol.
3. Establish state transitions for concurrent agent handoffs.

### Phase 3: Proactive Budget Guard & Auto-Repairing
1. Add strict budget limits parsing and active check gates on the CLI pipeline.
2. Implement auto-recovery repair hooks (`./helper.sh doctor --repair`).
