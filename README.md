# 🚀 Antigravity Agents (v5.0.0)

<div align="center">

**The Production-Grade, Autonomous Engineering Framework for Google Antigravity**  
*Optimized for Gemini 3.8 Flash (High) • Native Progressive Disclosure • Lifecycle Hooks • Multi-Agent Workspaces*

[![Version](https://img.shields.io/badge/version-5.0.0-blue.svg?style=flat-square)](https://github.com/rafaelghif/antigravity-agents/releases/tag/v5.0.0)
[![Platform](https://img.shields.io/badge/platform-Google_Antigravity_2.0_%26_CLI-8A2BE2.svg?style=flat-square)](https://antigravity.google/docs)
[![Model](https://img.shields.io/badge/optimized_for-Gemini_3.8_Flash_(High)-0052CC.svg?style=flat-square)](https://antigravity.google/docs/rules-workflows)
[![Skills](https://img.shields.io/badge/skills-64_Progressive_Skills-success.svg?style=flat-square)](#-autonomous-skills-suite)
[![Memory](https://img.shields.io/badge/memory-5--Tier_Architecture-orange.svg?style=flat-square)](#-5-tier-memory-management-architecture)
[![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)

</div>

---

## 🌟 What is Antigravity Agents v5?

**Antigravity Agents v5** represents a complete architectural evolution for the [antigravity-agents](https://github.com/rafaelghif/antigravity-agents) repository. Transitioning from script-heavy scaffolding in v4, **v5** adopts the official **Google Antigravity Customization Architecture**:

1. **Zero Hallucination Native Tooling**: Directly integrates with Antigravity's native primitives (`run_command`, `replace_file_content`, `view_file`, `invoke_subagent`, `manage_task`, `schedule`).
2. **Gemini 3.8 Flash (High) Optimization**: Designed for ultra-fast, deterministic, low-token pair programming following the **Caveman Principle** (terse technical precision) and **Ponytail Principle** (7-rung minimalist code ladder).
3. **64 Progressive Disclosure Skills**: Houses 64 modular engineering, testing, architectural, and token-saving skills that load dynamically on demand without polluting the main context window.
4. **5-Tier Memory Architecture**: Governed by `memory-management.md`, `CONTEXT.md`, ADRs (`docs/adr/`), and inter-session bridge handoffs (`.scratch/handoff.md` via `handoff` skill).
5. **First-Class Lifecycle Hooks**: Configured via `.agents/hooks.json` supporting `PreToolUse` (git guardrails) and `Stop` gates (`quality-gate` running `verify-on-stop.ps1`).
6. **Autonomous Subagent Workspaces**: Native DAG execution via `invoke_subagent` utilizing isolated workspace branches (`Workspace: "branch"` or `"share"`).
7. **Multi-VCS Model Context Protocol (MCP)**: Out-of-the-box configuration for **Gitea MCP** (stdio) and **GitHub MCP** (remote SSE) with zero-leak credential isolation (`.gitignore` sandboxing).
8. **Strict Workspace Isolation**: 100% scoped to `.agents/`. Zero machine-global pollution. Fully tested on Windows (PowerShell 5.1+) and cross-platform POSIX.

---

## ⚡ Quick Start via `npx`

Scaffold, audit, or inspect any repository with a single command:

```bash
# Scaffold Antigravity (.agents/, AGENTS.md, CONTEXT.md) into any repo
npx antigravity-agents init

# Run diagnostic environment health checks
npx antigravity-agents doctor

# Audit current workspace against Antigravity best practices
npx antigravity-agents audit

# Browse all 64 available progressive disclosure skills
npx antigravity-agents list
```

## 🏗️ Architecture Overview

```mermaid
flowchart TD
    User(["👤 User Request / Slash Command"]) --> Antigravity["Google Antigravity Engine (CLI / 2.0 / IDE)"]

    subgraph Context ["🧠 Context & Rule Precedence"]
        AGENTS["1. AGENTS.md (Root Guidelines, ≤12k chars)"]
        Rules["2. .agents/rules/*.md (trigger: always_on)"]
        Hooks["3. .agents/hooks.json (PreToolUse, PostToolUse, Stop)"]
        Plugins["4. .agents/plugins/ (Packaged MCP & Sidecars via plugins.json)"]
        MCP["5. .agents/mcp_config.json (GitHub & Gitea Tools)"]
        Skills["6. .agents/skills/ (Progressive Disclosure via skills.json)"]
    end

    Antigravity --> Context

    subgraph HooksEngine ["⚡ Lifecycle Event Hooks Engine"]
        PreTool["PreToolUse Hook (git-guardrails: blocks push/reset/clean)"]
        PostTool["PostToolUse Hook (auto-lint & format)"]
        StopHook["Stop Hook (verifies tests & background tasks before exit)"]
    end

    Antigravity --> HooksEngine

    subgraph SubagentsEngine ["🤖 Autonomous Subagents (invoke_subagent)"]
        Investigator["cavecrew-investigator (TypeName: research, Model: flash)"]
        Builder["cavecrew-builder (TypeName: self, Workspace: branch)"]
        Reviewer["cavecrew-reviewer / code-review (Two-Axis Reviewers)"]
    end

    Antigravity --> SubagentsEngine

    subgraph SidecarsEngine ["⚙️ Background Sidecars & Scheduled Tasks"]
        Sidecars["repo-health (Periodic git & branch hygiene monitor)"]
        CronSchedule["/schedule & schedule tool (One-shot and recurring timers)"]
    end

    Antigravity --> SidecarsEngine
```

---

## 📂 Repository Layout

```text
antigravity-agents/
├── .agents/
│   ├── hooks.json                     # Antigravity lifecycle hooks (PreToolUse git-guardrails, Stop quality-gate)
│   ├── hooks/                         # Executable hook scripts (block-dangerous-git.ps1, verify-on-stop.ps1)
│   ├── plugins.json                   # Explicit workspace plugin registration
│   ├── skills.json                    # Explicit workspace skills registration
│   ├── mcp_config.example.json        # Public sanitized template for Gitea and GitHub MCP
│   ├── plugins/                       # Workspace plugins packaging tools & background processes
│   │   └── workspace-integrations/    # Workspace integrations bundle (plugin.json, sidecars)
│   ├── rules/                         # Workspace-level rules with 'trigger: always_on'
│   │   ├── caveman.md                 # Ultra-compressed token communication protocol
│   │   ├── coding-standards.md        # Quality, SRP, error handling, targeted replacement
│   │   ├── git-workflow.md            # Conventional Commits and atomic changes
│   │   ├── ponytail.md                # 7-rung minimalist code ladder (YAGNI to one-liners)
│   │   └── memory-management.md       # 5-tier memory hierarchy & cross-session handoff protocol
│   └── skills/                        # 64 On-demand skills (Progressive disclosure via skills.json)
├── docs/                              # Project documentation & decision records
│   ├── adr/                           # Architectural Decision Records (0001-5-tier-memory)
│   ├── agents/                        # Agent skill configs (issue-tracker, domain, triage-labels)
│   ├── templates/                     # Standardized session handoff template
│   └── audit-checklist-64-skills.md   # Persistent 8-dimension audit checklist for all 64 skills
├── tests/                             # Automated verification suites (node --test)
│   └── memory-system.test.mjs         # Verified 64-skill criteria and memory architecture checks
├── .scratch/                          # Local session scratchpad & handoff staging (gitignored)
├── AGENTS.md                          # Root instructions unconditionally loaded per turn (<12k chars)
├── GEMINI.md                          # Pointer alias to AGENTS.md
├── CONTEXT.md                         # Living domain glossary & architectural boundaries
├── .gitignore                         # Quarantines PATs, credentials, .scratch/*, and local caches
└── README.md                          # Framework documentation
```

---

## ⚡ Autonomous Skills Suite

Skills are loaded into Antigravity via **progressive disclosure**: only names and descriptions are exposed initially. When a matching intent is recognized, Antigravity reads the target `SKILL.md` directly:

### 1. Minimalist Code & Token Reduction
- **`ponytail` / `ponytail-review` / `ponytail-audit`**: Enforces the 7-rung code ladder (YAGNI → Reuse → Standard Library → Native Platform → Dependency → One-Liner → Minimal Diff). Eliminates speculative abstractions.
- **`caveman` / `cavecrew` / `caveman-compress` / `caveman-commit`**: Compresses output and context to conserve tokens while preserving 100% technical fidelity.

### 2. Specification & Planning
- **`ask-matt`**: Meta-router recommending the best skill or workflow for any given task.
- **`grill-me` / `grill-with-docs` / `grilling`**: Relentless interactive interview stress-testing plans, requirements, and domain glossaries.
- **`to-spec`**: Synthesizes conversations into exhaustive technical specifications with test seams.
- **`to-tickets`**: Decomposes specs into vertical tracer-bullet tickets with dependency edges.
- **`wayfinder`**: Maps complex multi-session efforts into a map of frontier decisions under the fog of war.

### 3. Implementation & Verification
- **`tdd`**: Strict test-first loop (Red → Green → Refactor) enforcing pre-agreed seams.
- **`implement` / `implement-spec`**: Executes tickets across concurrent subagents in isolated branches (`Workspace: "branch"`).
- **`surgical-patch`**: Pinpoint bug fixing at the narrowest responsible layer without scope creep.
- **`diagnosing-bugs`**: Systematic scientific hypothesis testing for intermittent issues and regressions.
- **`code-review`**: Parallel two-axis review checking **Standards** (conventions & Fowler smells) and **Spec** (fidelity to requirements).

### 4. Safety & Delegation
- **`git-guardrails`**: Intercepts `run_command` in Antigravity to reject `push`, `reset --hard`, `clean -f`, and `branch -D`.
- **`handoff` / `subagent-handoff`**: Compacts sessions into structured handoffs and spins off background workers.
- **`triage`**: Triages issues and PRs through canonical states (`needs-triage`, `needs-info`, `ready-for-agent`, `ready-for-human`, `wontfix`).

---

## 🧠 5-Tier Memory Management Architecture

To prevent context window bloat, token waste, and attention degradation, Antigravity Agents v5 enforces a deterministic 5-Tier Memory model:

```
┌─────────────────────────────────────────────────────────────┐
│ Tier 1: Ephemeral Working Context (Intra-Session)           │ -> Context window & transcript.jsonl
├─────────────────────────────────────────────────────────────┤
│ Tier 2: Unconditional Directives (Cross-Session)            │ -> AGENTS.md, .agents/rules/*.md
├─────────────────────────────────────────────────────────────┤
│ Tier 3: Domain & Architectural Knowledge (Living Docs)      │ -> CONTEXT.md, docs/adr/*.md
├─────────────────────────────────────────────────────────────┤
│ Tier 4: Session Bridge Handoff (Inter-Session State)        │ -> .scratch/handoff.md via handoff skill
├─────────────────────────────────────────────────────────────┤
│ Tier 5: External Task Graph (Durable Frontier)              │ -> GitHub / Gitea Issues (to-tickets)
└─────────────────────────────────────────────────────────────┘
```

- **Intra-Session (Tier 1)**: Progressive disclosure keeps context lean; skills load on-demand via `view_file`.
- **Workspace Directives (Tier 2)**: `AGENTS.md` (<12k chars) and `.agents/rules/` (`trigger: always_on`) auto-injected every turn.
- **Domain Memory (Tier 3)**: Living domain glossary in `CONTEXT.md` and immutable decisions in `docs/adr/`.
- **Inter-Session Bridge (Tier 4)**: Before exiting, execute `handoff` to create `.scratch/handoff.md`. Fresh sessions rehydrate via `@handoff.md`.
- **Durable Task Graph (Tier 5)**: External source of truth in GitHub / Gitea issues managed via `to-tickets`, `wayfinder`, and `triage`.

---

## 🔌 Model Context Protocol (MCP) Setup

Antigravity Agents v5 natively supports workspace-level MCP servers.

Copy `.agents/mcp_config.example.json` to `.agents/mcp_config.json` (which is gitignored):

```bash
cp .agents/mcp_config.example.json .agents/mcp_config.json
```

Configure your credentials:

```json
{
  "mcpServers": {
    "github": {
      "serverUrl": "https://api.githubcopilot.com/mcp/",
      "headers": {
        "Authorization": "Bearer YOUR_GITHUB_PAT"
      }
    },
    "gitea": {
      "command": "gitea-mcp",
      "args": ["-t", "stdio"],
      "env": {
        "GITEA_HOST": "https://gitea.com",
        "GITEA_ACCESS_TOKEN": "YOUR_GITEA_PAT"
      }
    }
  }
}
```

- **Gitea MCP**: Runs locally via `gitea-mcp` stdio transport.
- **GitHub MCP**: Connects remotely via SSE.

---

## 🛡️ Git Guardrails & Security

Destructive git operations are blocked before execution by the Antigravity `PreToolUse` hook in `.agents/hooks.json`:

```powershell
# Tested on Windows PowerShell:
'{"toolCall":{"name":"run_command","args":{"CommandLine":"git push origin main"}}}' | powershell -File .agents/skills/git-guardrails/scripts/block-dangerous-git.ps1
# Returns: {"decision":"deny","reason":"BLOCKED: 'git push origin main' matches dangerous git pattern '\\bgit\\s+push\\b'..."}
```

---

## 🚀 Getting Started

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/rafaelghif/antigravity-agents.git
   cd antigravity-agents
   ```

2. **Open in Antigravity**:
   - Launch **Antigravity 2.0**, **Antigravity IDE**, or **Antigravity CLI** (`agy`):
     ```bash
     agy
     ```

3. **Verify Active Configuration**:
   - `AGENTS.md` is loaded automatically into the agent's context.
   - Run `/help` or ask the agent what workflows to use:
     ```text
     What workflows are available for implementing a new feature?
     ```
   - The agent will autonomously route through `ask-matt`, `to-spec`, `tdd`, or `implement-spec`.

---

## 📜 License & Credits

- **Author**: Muhammad Rafael Ghifari ([@rafaelghif](https://github.com/rafaelghif))
- **License**: [MIT](LICENSE)
- **Built For**: [Google Antigravity](https://antigravity.google)
