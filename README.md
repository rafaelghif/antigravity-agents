# Antigravity Agent Core (AAC) V4

[![Version](https://img.shields.io/badge/version-4.2.1-blue.svg)](AGENTS.md)
[![Status](https://img.shields.io/badge/status-production_ready-brightgreen.svg)](AGENTS.md)
[![Platform](https://img.shields.io/badge/platform-Antigravity_CLI-lightgrey.svg)](https://github.com/rafaelghifari/antigravity-agents)

**Enterprise-Grade Guardrails, Zero-Assumption Execution, and Quality Gates for Autonomous AI Coding Agents.**

Autonomous coding agents offer massive productivity boosts, but running them in unstructured repositories introduces severe risks: hallucinated architectures, credential leaks, messy commit histories, and exploding token budgets.

**Antigravity Agent Core (AAC) V4.2.1** solves this by enforcing a strict, token-optimized, skill-based workflow loop governed by a supreme constitution (`AGENTS.md`). Designed for the **Antigravity CLI (agy)**, AAC V4.2.1 ensures that AI-driven coding conforms exactly to professional engineering standards, handles edge cases autonomously, and never assumes anything.

> [!IMPORTANT]
> **100% Declarative & Skill-Based**: AAC V4.2.1 abandons clunky bash scripts in favor of AI-native `.agents/skills/`. All configurations, plans, schemas, and execution logs are isolated securely under the `.agents/` directory.


> [!WARNING]
> **Disclaimer of Liability**: This software is provided "as is", without warranty of any kind. Autonomous AI agents run processes and modify files directly in your local environment. While AAC V4.2 establishes security hooks and quality gates, the user is solely responsible for reviewing and approving all commands, code modifications, and commits. The authors assume no liability for code regressions, data loss, credential exposures, or system errors resulting from agent activities.

---

## ⚡ What's New in V4.2?

| The AI Coding Risk | The AAC V4.2 Solution |
| :--- | :--- |
| **Agent Amnesia & Bloat** | **Hermes Protocol & 6 Core Domain Skills**: Consolidates 15 redundant skills into 6 lean domain skills (`code-engineer`, `system-architect`, `quality-assurance`, `devops-manager`, `security-docs-auditor`, `system-janitor`), reducing token bloat by >60%. |
| **Race Conditions & Skipped Steps** | **Multi-Agent Execution Topologies**: Supports Parallel Swarms (with Synchronization Barriers) for independent audits and Sequential Stage-Gated Pipelines for feature dev. |
| **Language Limitation** | **Universal Polyglot Support**: Native best practices for TypeScript, Python, Go, Rust, PHP, Java/Kotlin, C#/.NET, Dart/Flutter, C/C++, Swift, Elixir, and legacy ASP/VB6. |
| **Hallucination & Snippet Blindness** | **Zero-Assumption & Anti-Snippet Policy**: Prohibits guessing fields or inferring data structures from partial snippet views. Enforces mandatory full symbol inspection. |
| **Secret Leaks** | **Zero Secrets & SAST Enforcement**: Strict environment variable substitution (`${GITHUB_PAT}`, `${GITEA_PAT}`) and CVSS $\ge 7.0$ vulnerability blocking. |

---

## 🚀 Core Skills (6 Consolidated Domain Modules)

AAC V4.2 operates using a dynamic arsenal of 6 core modular **Skills** located in `.agents/skills/`:

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
To apply AAC V4.2 manually to any existing project, clone this repository and copy the core files over to your target project's root directory:


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
AAC V4 relies on Model Context Protocol (MCP) servers to interact with version control safely and execute the `git-workflow` skill.

We provide a ready-to-use sample configuration file:
```bash
cp .agents/mcp_config.json.example .agents/mcp_config.json
```
Edit `.agents/mcp_config.json` to insert your specific Personal Access Tokens (PAT) and your Gitea server URL (e.g., `http://localhost:3000`).

- **GitHub MCP**: Connects via Copilot's Remote Server-Sent Events (SSE).
- **Gitea MCP**: Connects via HTTP mode (e.g., `http://10.137.1.87:8081/mcp`) to a Gitea instance hosting the MCP endpoint. Once active, AAC V4's `git-workflow` skill will automatically detect it and enforce strict time-tracking.

---

## 📂 Directory Layout

- `AGENTS.md`: The "Constitution" and supreme ruleset.
- `.agents/brain/`: Permanent memory (`schema.md`, `state.json`, `mcp-registry.json`, `rules.md`).
- `.agents/incidents/`: Post-mortem incident reports for failed tasks or timeouts.
- `.agents/plans/`: Lightweight sequential task checklists.
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
