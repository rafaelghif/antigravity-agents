# Antigravity Agent Core (AAC) V4.3

[![Version](https://img.shields.io/badge/version-4.3.0-blue.svg)](AGENTS.md)
[![Status](https://img.shields.io/badge/status-production_ready-brightgreen.svg)](AGENTS.md)
[![Platform](https://img.shields.io/badge/platform-Antigravity_CLI-lightgrey.svg)](https://github.com/rafaelghifari/antigravity-agents)

**Enterprise-Grade Guardrails, Task-Driven Execution Engine, and Deterministic Quality Gates for Autonomous AI Coding Agents.**

Autonomous coding agents offer massive productivity boosts, but running them in unstructured repositories introduces severe risks: hallucinated architectures, context amnesia across session switches, skipped workflow gates, and exploding token budgets.

**Antigravity Agent Core (AAC) V4.3.0** solves this by introducing a **Deterministic Task-Driven & File-Backed Execution Engine** governed by a supreme constitution (`AGENTS.md`). Designed for the **Antigravity CLI (agy)**, AAC V4.3.0 ensures that AI-driven coding conforms exactly to professional engineering standards, handles session interrupts seamlessly, and never assumes anything.

> [!IMPORTANT]
> **100% Task-Driven & File-Backed**: AAC V4.3.0 eliminates volatile state.json tracking in favor of physical, granular markdown plan checklists (`.agents/plans/*.md`) and POSIX directory-based file locking (`.agents/locks/`).

> [!WARNING]
> **Disclaimer of Liability**: This software is provided "as is", without warranty of any kind. Autonomous AI agents run processes and modify files directly in your local environment. While AAC V4.3 establishes security hooks and quality gates, the user is solely responsible for reviewing and approving all commands, code modifications, and commits. The authors assume no liability for code regressions, data loss, credential exposures, or system errors resulting from agent activities.

---

## ⚡ What's New in V4.3?

| The AI Coding Risk | The AAC V4.3 Solution |
| :--- | :--- |
| **Session Amnesia & State Loss** | **Task-Driven Plan Checklists (`.agents/plans/`)**: Replaces volatile state pointers with physical, file-backed micro-task checklists. Enables instant recovery from session switches or crashes without re-implementing finished code. |
| **Race Conditions in Multi-Agent Swarms** | **POSIX Directory-Based Mutex Locking (`.agents/locks/`)**: Implements OS-level atomic directory locking (`mkdir -p .agents/locks/<hash>.lock`) with 60s auto-expiration to guarantee zero TOCTOU collisions. |
| **LLM Workflow Bypass & Eagerness** | **Strict Pre-Execution Hard-Lock Gate**: Prohibits any source code edits until (1) a granular plan file exists in `.agents/plans/` AND (2) a dedicated Git branch (`task/<slug>`) is created. |
| **Lost /grill-me & Interview Decisions** | **Decisions & Architectural Trade-offs Ledger**: Forces mandatory logging of user directives, constraints, and `/grill-me` interview agreements directly into the plan file's permanent header. |
| **LLM Batching & False Completion** | **Zero-Batching & Empirical Verification Gate**: Forces single micro-task execution per turn with mandatory physical CLI output (`exit code 0` from `npm test` or `tsc`) before marking tasks `- [x]`. |
 |

---

## 🚀 Core Skills (6 Consolidated Domain Modules)

AAC V4.3 operates using a dynamic arsenal of 6 core modular **Skills** located in `.agents/skills/`:

- **`code-engineer`**: Universal clean code enforcer (SOLID/DRY) across 14+ language families and scientific log-driven debugging.
- **`system-architect`**: Single authority for architectural impact auditing, DB schema governance (`.agents/brain/schema.md`), and mock data synthesis.
- **`quality-assurance`**: Automated test suite execution, WCAG 2.1 AA UI/A11y review, and 5-dimension performance profiling (CPU, I/O, DB, Memory, Network).
- **`devops-manager`**: End-to-end Git version control lifecycle (Issue, Branching, PRs), branch janitor cleanup, and local CI pipeline simulation (`act`).
- **`security-docs-auditor`**: SAST vulnerability scanning, secret leakage prevention, and technical documentation sync (OpenAPI & SemVer CHANGELOG).
- **`system-janitor`**: Token budget optimization (>80% compaction), ephemeral scratch purging, and background process timeout management.


---

## 🛠️ Quick Installation & Setup

### Option A: Quick 1-Line Install (Linux / macOS / WSL)
Run this single command inside your project root directory:

```bash
curl -fsSL https://raw.githubusercontent.com/rafaelghifari/antigravity-agents/main/install.sh | bash
```

### Option B: Quick 1-Line Install (Windows PowerShell)
Run this single command inside your project root directory in PowerShell:

```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; iwr -useb https://raw.githubusercontent.com/rafaelghifari/antigravity-agents/main/install.ps1 | iex
```

### Option C: Manual Integration
To apply AAC V4.3 manually to any existing project, clone this repository and copy the core files over to your target project's root directory:


```bash
# Clone the AAC repository
git clone https://github.com/rafaelghifari/antigravity-agents.git
cd antigravity-agents

# Copy the core constitution, skills, and hygiene configs to your target project
cp AGENTS.md /path/to/your/project/
cp .gitignore /path/to/your/project/
cp -r .agents /path/to/your/project/
```


### 2. Configure MCP Servers (Optional but Recommended)
AAC V4.3 relies on Model Context Protocol (MCP) servers to interact with version control safely and execute the `devops-manager` skill.

We provide a ready-to-use sample configuration file:
```bash
cp .agents/mcp_config.json.example .agents/mcp_config.json
```
Edit `.agents/mcp_config.json` to insert your specific Personal Access Tokens (PAT) and your Gitea server URL (e.g., `http://localhost:3000`).

- **GitHub MCP**: Connects via Copilot's Remote Server-Sent Events (SSE).
- **Gitea MCP**: Connects via HTTP mode (e.g., `http://10.137.1.87:8081/mcp`) to a Gitea instance hosting the MCP endpoint. Once active, AAC V4.3's `devops-manager` skill will automatically detect it and enforce strict time-tracking.

---

## 📂 Directory Layout

- `AGENTS.md`: The "Constitution" and supreme ruleset.
- `.agents/brain/`: Permanent memory (`schema.md`, `rules.md`, `env-required.json`, `audit.jsonl`).
- `.agents/`: Global config & MCP servers (`config.json`, `mcp_config.json`).
- `.agents/locks/`: Atomic POSIX directory-based mutex locks (`.agents/locks/<hash>.lock`).
- `.agents/incidents/`: Post-mortem incident reports for failed tasks or timeouts.
- `.agents/plans/`: Granular markdown execution checklists (Single Source of Truth).
- `.agents/scratch/`: Ephemeral/short-term notes and debugging context.
- `.agents/skills/`: The 6 core operational skills listed above.


---

## ⚡ Slash Commands (Anti-Hallucination)

Start your prompt with these commands to maximize autonomy:

| Command | Best For | Description |
| :--- | :--- | :--- |
| **`/goal`** | `Long-running autonomy` | Forces the agent into a persistent loop to hit complex milestones. |
| **`/grill-me`** | `Requirements gathering` | The agent pauses coding and interviews you with targeted questions. |
| **`/teamwork-preview`** | `Parallel execution` | Divides massive tasks and spawns multiple sub-agents. |
| **`/plan`** | `Step-by-step logic` | Outputs a rigorous step-by-step checklist before proceeding. |
| **`/learn`** | `Self-Correction` | Documents a new pattern in `rules.md` or generates a new skill. |
