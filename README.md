<div align="center">

# ⚡ Antigravity Agent Core (AAC) V4.3

[![Version](https://img.shields.io/badge/version-4.3.3-blue.svg?style=for-the-badge&logo=git&logoColor=white)](https://github.com/rafaelghif/antigravity-agents/releases/tag/v4.3.3)
[![Status](https://img.shields.io/badge/status-production_ready-brightgreen.svg?style=for-the-badge&logo=checkmarx&logoColor=white)](https://github.com/rafaelghif/antigravity-agents/releases/tag/v4.3.3)
[![Platform](https://img.shields.io/badge/platform-Antigravity_CLI-8A2BE2.svg?style=for-the-badge&logo=google&logoColor=white)](https://antigravity.google/docs/cli/overview)
[![Architecture](https://img.shields.io/badge/architecture-AAC_V4.3_Deterministic-orange.svg?style=for-the-badge&logo=diagramsdotnet&logoColor=white)](https://github.com/rafaelghif/antigravity-agents)

**Enterprise-Grade Guardrails, Task-Driven Execution Engine, and Deterministic Quality Gates for Autonomous AI Coding Agents.**

[Features](#-key-architecture--core-capabilities) • [Domain Skills](#-6-consolidated-core-domain-skills) • [Installation](#%EF%B8%8F-quick-installation) • [Directory Structure](#-system-directory-structure) • [Slash Commands](#-antigravity-native-slash-commands)

</div>

---

## 💡 What is Antigravity Agent Core?

Autonomous AI coding agents offer massive productivity boosts, but running them in un-governed repositories introduces severe friction: hallucinated architectures, context amnesia across session switches, skipped workflow gates, robotic tone, and exploding token budgets.

**Antigravity Agent Core (AAC) V4.3.3** establishes a **Deterministic Task-Driven & File-Backed Execution Protocol** governed by a supreme constitution (`AGENTS.md`). Built natively for **Google Antigravity**, AAC V4.3 ensures AI-driven coding conforms exactly to senior engineering standards, recovers seamlessly from interrupts, and pair-programs like a real human partner.

> [!IMPORTANT]
> **100% Task-Driven & File-Backed**: AAC V4.3.3 eliminates volatile state tracking in favor of physical, granular markdown plan checklists (`.agents/plans/*.md`), zero-assumption contracts (`.agents/brain/schema.md`), and POSIX directory mutex locks (`.agents/locks/`).

---

## ⚡ Key Architecture & Core Capabilities

```
       +-------------------------------------------------------------------+
       |                       Supreme Constitution                        |
       |                            (AGENTS.md)                            |
       +-------------------------------------------------------------------+
                                         |
         +-------------------------------+-------------------------------+
         |                               |                               |
         v                               v                               v
+------------------+           +-------------------+           +-------------------+
|   Memory Boot    |           |  Task Execution   |           |  POSIX File Lock  |
| (.agents/brain/) |           | (.agents/plans/)  |           | (.agents/locks/)  |
| - soul.md        |           | - Granular Plans  |           | - Atomic Locks    |
| - rules.md       |           | - Zero-Batching   |           | - Anti-TOCTOU     |
| - schema.md      |           | - Build/Test Gate |           | - 60s Expiration  |
+------------------+           +-------------------+           +-------------------+
```

| Architectural Challenge | The AAC V4.3 Solution |
| :--- | :--- |
| **Session Amnesia & State Loss** | **Task-Driven Plan Checklists (`.agents/plans/`)**: File-backed micro-task checklists enable instant recovery across session switches or crashes without re-implementing finished code. |
| **Robotic AI Tone & Yes-Man Bias** | **Humanized Senior Co-Pilot (`.agents/brain/soul.md`)**: Replaces canned AI fluff with a warm, authentic, crisp senior engineering partner voice while maintaining uncompromising technical pushback. |
| **Swarm Race Conditions** | **POSIX Directory Mutex Locks (`.agents/locks/`)**: OS-level atomic directory locks (`mkdir -p .agents/locks/<hash>.lock`) with 60s auto-expiration guarantee zero TOCTOU collisions. |
| **LLM Eagerness & Workflow Bypass** | **Tier-Aware Pre-Execution Gate**: T1 patches (`< 50 lines`, single file) take a fast path; T2/T3 features and refactors are prohibited from code edits until (1) a granular plan file exists in `.agents/plans/` AND (2) a dedicated Conventional branch (`<type>/issue-<N>-<slug>`) is checked out. |
| **LLM Batching & False Completion** | **Zero-Batching & Empirical Verification**: Enforces single micro-task execution per turn with mandatory physical CLI output (`exit code 0` from `npm test` or `tsc`) before marking `- [x]`. |

---

## 🚀 6 Consolidated Core Domain Skills

AAC V4.3 operates via 6 specialized domain skills inside `.agents/skills/`:

| Skill Module | Operational Scope & Responsibilities |
| :--- | :--- |
| 🛠️ **`code-engineer`** | Universal clean code enforcer (SOLID/DRY) across 14+ language families and scientific log-driven debugging. |
| 🏗️ **`system-architect`** | Single authority for architectural impact auditing, DB schema governance (`.agents/brain/schema.md`), and mock data synthesis. |
| 🧪 **`quality-assurance`** | Automated test suite execution, WCAG 2.1 AA UI/A11y review, and 5-dimension performance profiling (CPU, I/O, DB, Memory, Network). |
| 🔀 **`devops-manager`** | End-to-end Git version control lifecycle (Issue, Branching, PRs), branch janitor cleanup, and local CI pipeline simulation (`act`). |
| 🛡️ **`security-docs-auditor`** | SAST vulnerability scanning, secret leakage prevention, and technical documentation sync (OpenAPI & SemVer CHANGELOG). |
| 🧹 **`system-janitor`** | Token budget optimization (>80% compaction), ephemeral scratch purging, and background process timeout management. |

---

## 🛠️ Quick Installation

### Option A: Linux / macOS / WSL (1-Line Quick Install)
```bash
curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/install.sh | bash
```

### Option B: Windows PowerShell (1-Line Quick Install)
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; iwr -useb https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/install.ps1 | iex
```

### Option C: Manual Scaffolding
```bash
git clone https://github.com/rafaelghif/antigravity-agents.git
cd antigravity-agents

# Copy core constitution and agents directory into your project root
cp AGENTS.md /path/to/your/project/
cp -r .agents /path/to/your/project/
```

---

## 📂 System Directory Structure

Below is the verified, authoritative layout of the `.agents/` engine and root files:

```
.
├── AGENTS.md                      # Supreme Constitution & AAC v4.3 Operational Directive
├── .env.example                   # Environment Variable Template (GitHub/Gitea Tokens)
├── install.sh                     # Linux/macOS One-Line Installer Script
├── install.ps1                    # Windows PowerShell One-Line Installer Script
├── LICENSE                        # MIT License
├── CHANGELOG.md                   # Semantic Version History
└── .agents/                       # Agentic AI Engine & Central Nervous System
    ├── config.json                # Master Numerical Bounds, Timeouts & Swarm Rules
    ├── mcp_config.json            # Model Context Protocol (MCP) Server Declarations (gitignored, local)
    ├── mcp_config.json.example    # MCP Setup Sample Template
    ├── TASK_TEMPLATE.md           # Standard Granular Task Execution Plan Template
    ├── brain/                     # Permanent Memory & Operational Contracts
    │   ├── soul.md                # Senior Co-Pilot Persona, Warm Tone & Oath
    │   ├── rules.md               # Persisted Project Invariants & User Lessons
    │   ├── schema.md              # Single Source of Truth DB & System Schemas
    │   ├── env-required.json      # Mandatory Secret & Environment Declarations
    │   ├── audit.jsonl            # Local Task Execution & Token Audit Trail (gitignored)
    │   └── schemas/               # Domain-Specific Extended Schemas
    ├── plans/                     # Granular Markdown Task Plan Checklists (Single Source of Truth)
    ├── locks/                     # POSIX Directory-Based Mutex Locks (<hash>.lock/owner.json)
    ├── incidents/                 # Post-Mortem Incident & Abort Reports
    ├── scratch/                   # Ephemeral Intermediate Scratchpad Workspace
    ├── common/                    # Shared Helper Protocols (utils.md)
    └── skills/                    # 6 Core Executable Domain Modules
        ├── code-engineer/        # SKILL.md
        ├── system-architect/     # SKILL.md
        ├── quality-assurance/    # SKILL.md
        ├── devops-manager/       # SKILL.md
        ├── security-docs-auditor/# SKILL.md
        └── system-janitor/       # SKILL.md
```

---

## ⚡ Antigravity Native Slash Commands

Maximize workflow autonomy using native Antigravity slash commands:

| Command | Best For | Description |
| :--- | :--- | :--- |
| **`/goal`** | `Long-running autonomy` | Forces the agent into a persistent loop to hit complex milestones. |
| **`/grill-me`** | `Requirements gathering` | The agent pauses coding and interviews you with targeted questions. |
| **`/teamwork-preview`** | `Parallel execution` | Divides massive tasks and spawns multiple sub-agents. |
| **`/plan`** | `Step-by-step logic` | Outputs a rigorous step-by-step checklist before proceeding. |
| **`/learn`** | `Self-Correction` | Documents a new pattern in `rules.md` or generates a new skill. |

---

<div align="center">

**Crafted for Antigravity AI Engineers** • Standardized under AAC v4.3 Protocol

</div>
