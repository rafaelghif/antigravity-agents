<div align="center">

# ⚡ Antigravity Agent Core (AAC) V4.3

[![Version](https://img.shields.io/badge/version-4.3.0-blue.svg?style=for-the-badge)](https://github.com/rafaelghif/antigravity-agents/releases/tag/v4.3.0)
[![Status](https://img.shields.io/badge/status-production_ready-brightgreen.svg?style=for-the-badge)](https://github.com/rafaelghif/antigravity-agents/releases/tag/v4.3.0)
[![Platform](https://img.shields.io/badge/platform-Antigravity_CLI-lightgrey.svg?style=for-the-badge)](https://antigravity.google/docs/cli/overview)
[![Architecture](https://img.shields.io/badge/architecture-AAC_V4.3_Deterministic-orange.svg?style=for-the-badge)](https://github.com/rafaelghif/antigravity-agents)

**Enterprise-Grade Guardrails, Task-Driven Execution Engine, and Deterministic Quality Gates for Autonomous AI Coding Agents.**

</div>

---

### 💡 Why Antigravity Agent Core?

Autonomous AI coding agents offer massive productivity boosts, but running them in un-governed repositories introduces severe friction: hallucinated architectures, context amnesia across session switches, skipped workflow gates, robotic tone, and exploding token budgets.

**Antigravity Agent Core (AAC) V4.3.0** solves this by establishing a **Deterministic Task-Driven & File-Backed Execution Protocol** governed by a supreme constitution (`AGENTS.md`). Built natively for **Google Antigravity**, AAC V4.3 ensures AI-driven coding conforms exactly to senior engineering standards, recovers seamlessly from interrupts, and pair-programs like a real human partner.

> [!IMPORTANT]
> **100% Task-Driven & File-Backed**: AAC V4.3.0 eliminates volatile tracking in favor of physical, granular markdown plan checklists (`.agents/plans/*.md`), zero-assumption contracts (`.agents/brain/schema.md`), and POSIX directory mutex locks (`.agents/locks/`).

---

## ⚡ Key Architecture & Core Capabilities

| Architectural Challenge | The AAC V4.3 Solution |
| :--- | :--- |
| **Session Amnesia & State Loss** | **Task-Driven Plan Checklists (`.agents/plans/`)**: File-backed micro-task checklists enable instant recovery across session switches or crashes without re-implementing finished code. |
| **Robotic AI Tone & Yes-Man Bias** | **Humanized Senior Co-Pilot (`.agents/brain/soul.md`)**: Replaces canned AI fluff with a warm, authentic, crisp senior engineering partner voice while maintaining uncompromising technical pushback. |
| **Swarm Race Conditions** | **POSIX Directory Mutex Locks (`.agents/locks/`)**: OS-level atomic directory locks (`mkdir -p .agents/locks/<hash>.lock`) with 60s auto-expiration guarantee zero TOCTOU collisions. |
| **LLM Eagerness & Workflow Bypass** | **Strict Pre-Execution Gate**: Prohibits code edits until (1) a granular plan file exists in `.agents/plans/` AND (2) a dedicated Git branch (`task/<slug>`) is checked out. |
| **LLM Batching & False Completion** | **Zero-Batching & Empirical Verification**: Enforces single micro-task execution per turn with mandatory physical CLI output (`exit code 0` from `npm test` or `tsc`) before marking `- [x]`. |

---

## 🚀 6 Consolidated Core Domain Skills

AAC V4.3 operates via 6 specialized domain skills inside `.agents/skills/`:

```
.agents/skills/
├── code-engineer/          # Clean Code (SOLID/DRY) & Polyglot Scientific Debugging
├── system-architect/       # Architectural Blast Radius & DB Schema Governance
├── quality-assurance/      # Test Suites, WCAG 2.1 AA UI/A11y & 5-Dim Perf Profiling
├── devops-manager/         # Git Lifecycle (Issues, Branching, PRs) & Local CI Simulation
├── security-docs-auditor/  # SAST Scanning, Secret Leak Prevention & OpenAPI/SemVer Sync
└── system-janitor/         # Token Budget Optimization & Ephemeral Scratch Purging
```

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

```
├── AGENTS.md             # Supreme Workspace Directive & Constitution (AAC v4.3)
└── .agents/
    ├── brain/            # Permanent Memory & Operational Contracts
    │   ├── soul.md       # Persona, Humanized Senior Partner Tone & Oath
    │   ├── rules.md      # Persisted Invariants & Project Lessons
    │   ├── schema.md     # Single Source of Truth DB & System Schemas
    │   └── audit.jsonl   # Immutable Task Execution Audit Log
    ├── config.json       # Master Numerical Bounds, Timeouts & Swarm Rules
    ├── TASK_TEMPLATE.md  # Standard Granular Task Execution Plan Template
    ├── plans/            # Granular Task Plan Checklists (Single Source of Truth)
    ├── locks/            # Atomic POSIX Directory Mutex Locks
    ├── scratch/          # Ephemeral Temporary Intermediate Workspace
    └── skills/           # 6 Core Executable Domain Modules
```

---

## ⚡ Antigravity Native Slash Commands

Maximize workflow autonomy using native Antigravity slash commands:

- **`/goal`**: Launch long-running overnight autonomous loops with deep verification.
- **`/grill-me`**: Pause coding and initiate an interactive alignment interview to clarify design trade-offs.
- **`/plan`**: Generate a structured step-by-step micro-task checklist before execution.
- **`/learn`**: Auto-document newly discovered engineering patterns into `rules.md` or workspace skills.

---

<div align="center">

**Crafted for Antigravity AI Engineers** • Standardized under AAC v4.3 Protocol

</div>
