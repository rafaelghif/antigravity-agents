<div align="center">

<img src="assets/banner.png" alt="AAC (Antigravity Agent Core) Banner" width="100%" />

# AAC (Antigravity Agent Core)

**Minimalist autonomous engineering framework for Google Antigravity.**  
*Engineered for Gemini 3.8 Flash (High) • Native Progressive Disclosure • Lifecycle Hooks • Multi-Agent Workspaces*

<p align="center">
  <a href="https://github.com/rafaelghif/antigravity-agents-core/releases/tag/v5.0.1"><img src="https://img.shields.io/badge/version-5.0.1-blue.svg?style=for-the-badge&logo=git" alt="Version 5.0.1" /></a>
  <a href="https://antigravity.google/docs"><img src="https://img.shields.io/badge/platform-Google_Antigravity_2.0-8A2BE2.svg?style=for-the-badge&logo=google" alt="Platform" /></a>
  <a href="https://antigravity.google/docs/rules-workflows"><img src="https://img.shields.io/badge/optimized_for-Gemini_3.8_Flash-0052CC.svg?style=for-the-badge&logo=googlecloud" alt="Gemini 3.8 Flash" /></a>
  <a href="#-autonomous-skills-suite"><img src="https://img.shields.io/badge/skills-64_verified-success.svg?style=for-the-badge" alt="64 Skills" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg?style=for-the-badge" alt="License: MIT" /></a>
</p>

<p align="center">
  <a href="#-quick-start-multi-platform">Quick Start</a> •
  <a href="#-architecture-overview">Architecture</a> •
  <a href="#-repository-layout">Repository Layout</a> •
  <a href="#-autonomous-skills-suite">Skill Catalog</a> •
  <a href="#-5-tier-memory-management">Memory System</a> •
  <a href="#-lifecycle-hooks--security">Lifecycle Hooks</a> •
  <a href="#-model-context-protocol-mcp">MCP Setup</a>
</p>

</div>

---

## ⚡ Overview

**AAC (Antigravity Agent Core)** is a minimalist autonomous engineering framework built for the **Google Antigravity Customization Architecture**. It provides focused pair programming, autonomous multi-agent task execution, and progressive context disclosure without token waste or hallucinated tooling.

<table>
  <tr>
    <td width="33%" align="center">
      <h3>🚀 Native Tool Calling</h3>
      <p>Seamless execution with Google Antigravity primitives: <code>run_command</code>, <code>replace_file_content</code>, <code>view_file</code>, and <code>invoke_subagent</code>.</p>
    </td>
    <td width="33%" align="center">
      <h3>🧠 Minimalist & Terse</h3>
      <p>Tailored for Gemini 3.8 Flash (High) via <b>Caveman Protocol</b> (fluff-free precision) and the 7-rung <b>Ponytail Ladder</b> (YAGNI to one-liners).</p>
    </td>
    <td width="33%" align="center">
      <h3>🔒 Zero Global Pollution</h3>
      <p>Strictly workspace-scoped within <code>.agents/</code>. Zero machine-global pollution (<code>~/.gemini/config/</code>) and zero <code>package.json</code> pollution.</p>
    </td>
  </tr>
</table>

---

## ⚡ Quick Start (Multi-Platform)

Install AAC into **any existing project** (Python, Go, Rust, Node, Java, PHP, C++) with a single command:

### Option 1: Universal NPX (Any OS with Node.js)
```bash
# Via npm registry:
npx @rafaelghif/aac-core init

# Or directly from GitHub:
npx github:rafaelghif/antigravity-agents-core init
```

### Option 2: Standalone Windows PowerShell (Zero Node.js Prerequisite)
```powershell
irm https://raw.githubusercontent.com/rafaelghif/antigravity-agents-core/main/install.ps1 | iex
```

### Option 3: Standalone Linux / macOS (Zero Node.js Prerequisite)
```bash
curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents-core/main/install.sh | bash
```

> [!IMPORTANT]
> **Zero Package.json Pollution Guarantee**: The installer will **NEVER** create, overwrite, or mutate `package.json` in your target repository. It cleanly scaffolds `.agents/`, `AGENTS.md`, and `CONTEXT.md`, and appends ignore rules to your `.gitignore`.

---

## 🏗️ Architecture Overview

The framework coordinates context precedence, lifecycle hooks, autonomous subagent graphs, and memory tiers:

```mermaid
flowchart TD
    User(["👤 User Request / Slash Command"]) --> Antigravity["Google Antigravity Engine (CLI / 2.0 / IDE)"]

    subgraph ContextHierarchy ["🧠 Context Precedence (AGENTS.md)"]
        AGENTS["1. AGENTS.md (Root Guidelines, ≤12k chars)"]
        Rules["2. .agents/rules/*.md (trigger: always_on)"]
        Hooks["3. .agents/hooks.json (PreToolUse, PostToolUse, Stop)"]
        Plugins["4. .agents/plugins/ (Packaged MCP & Sidecars)"]
        MCP["5. .agents/mcp_config.json (GitHub & Gitea Tools)"]
        Skills["6. .agents/skills/ (Progressive Disclosure)"]
    end

    Antigravity --> ContextHierarchy

    subgraph LifecycleEngine ["⚡ Lifecycle Event Hooks Engine"]
        PreTool["PreToolUse Hook (git-guardrails: blocks push / reset / clean)"]
        PostTool["PostToolUse Hook (automated linting & validation)"]
        StopHook["Stop Quality Gate (blocks exit on failing tests)"]
    end

    Antigravity --> LifecycleEngine

    subgraph SubagentsGraph ["🤖 Autonomous Subagents (invoke_subagent)"]
        Investigator["cavecrew-investigator (TypeName: research, Model: flash)"]
        Builder["cavecrew-builder (TypeName: self, Workspace: branch)"]
        Reviewer["cavecrew-reviewer / code-review (Two-Axis Reviewers)"]
    end

    Antigravity --> SubagentsGraph

    subgraph SidecarsEngine ["⚙️ Background Sidecars & Scheduled Tasks"]
        Sidecars["repo-health (Periodic git & branch hygiene monitor)"]
        CronSchedule["schedule tool (One-shot and recurring timers)"]
    end

    Antigravity --> SidecarsEngine
```

---

## 📂 Repository Layout

```text
antigravity-agents/
├── assets/                            # Framework visual assets & documentation banners
│   └── banner.png                     # Vector branding banner
├── .agents/                           # Workspace configuration (Strictly isolated)
│   ├── hooks.json                     # Antigravity lifecycle hooks (PreToolUse, Stop)
│   ├── hooks/                         # Cross-platform hooks (block-dangerous-git.cjs, verify-on-stop.cjs)
│   ├── plugins.json                   # Explicit workspace plugin registration
│   ├── skills.json                    # Explicit workspace skills registration (64 skills)
│   ├── mcp_config.example.json        # Sanitized template for Gitea and GitHub MCP
│   ├── plugins/                       # Workspace plugins packaging tools & sidecars
│   │   └── workspace-integrations/    # Workspace integrations bundle
│   ├── rules/                         # Workspace-level rules with 'trigger: always_on'
│   │   ├── caveman.md                 # Ultra-compressed token communication protocol
│   │   ├── coding-standards.md        # SRP, fail-fast, and targeted replacement rules
│   │   ├── git-workflow.md            # Conventional Commits and atomic changes
│   │   ├── ponytail.md                # 7-rung minimalist code ladder (YAGNI to one-liners)
│   │   └── memory-management.md       # 5-tier memory hierarchy & cross-session protocol
│   └── skills/                        # 64 On-demand skills (Progressive disclosure)
├── bin/                               # Universal CLI executable
│   └── cli.mjs                        # Multi-platform installer (init, audit, doctor, list)
├── docs/                              # Framework documentation & decision records
│   ├── adr/                           # Architectural Decision Records (0001-memory, 0002-node-hooks)
│   ├── agents/                        # Skill specifications (issue-tracker, domain, triage-labels)
│   ├── templates/                     # Standardized session handoff template
│   └── audit-checklist-64-skills.md   # Persistent 8-dimension audit checklist for all 64 skills
├── tests/                             # Automated verification suites (node --test)
│   ├── memory-system.test.mjs         # Verified 64-skill criteria and memory architecture
│   └── cli.test.mjs                   # CLI tests (including zero-package.json pollution test)
├── install.ps1                        # Standalone Windows PowerShell 1-liner installer (Zero Node)
├── install.sh                         # Standalone Linux/macOS curl 1-liner installer (Zero Node)
├── package.json                       # Framework manifest for npm/npx distribution
├── .scratch/                          # Local session scratchpad & handoff staging (gitignored)
├── AGENTS.md                          # Root instructions unconditionally loaded per turn (<12k chars)
├── GEMINI.md                          # Pointer alias to AGENTS.md
└── CONTEXT.md                         # Living domain glossary & architectural boundaries
```

---

## 🎯 Autonomous Skills Suite

Skills are loaded into Antigravity via **progressive disclosure**: only names and descriptions are exposed in the initial context. When a user intent or slash command is matched, the agent reads the target `SKILL.md` directly via `view_file`.

<details>
<summary><b>1. Specification, Planning & Product (Click to expand)</b></summary>

| Skill | Description | Primary File |
| :--- | :--- | :--- |
| `ask-matt` | Meta-router recommending the best skill or workflow for any given task | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/ask-matt/SKILL.md) |
| `grill-me` | Relentless interactive interview stress-testing plans, requirements, and edge cases | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/grill-me/SKILL.md) |
| `grill-with-docs` | Stress-tests a plan while simultaneously documenting ADRs and domain glossaries | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/grill-with-docs/SKILL.md) |
| `to-spec` | Synthesizes conversations and codebase context into complete technical specifications | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/to-spec/SKILL.md) |
| `to-tickets` | Decomposes specs into vertical tracer-bullet tickets with dependency edges | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/to-tickets/SKILL.md) |
| `wayfinder` | Maps large multi-session efforts into a map of frontier decisions under fog of war | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/wayfinder/SKILL.md) |
| `to-questionnaire` | Turns decisions and missing requirements into structured questionnaires | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/to-questionnaire/SKILL.md) |
| `prototype` | Builds throwaway prototypes to sanity check state models and user experience | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/prototype/SKILL.md) |

</details>

<details>
<summary><b>2. Implementation, TDD & Verification (Click to expand)</b></summary>

| Skill | Description | Primary File |
| :--- | :--- | :--- |
| `tdd` | Test-driven development (Red → Green → Refactor) enforcing pre-agreed seams | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/tdd/SKILL.md) |
| `implement` | Implements feature work from tickets or specifications using strict TDD | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/implement/SKILL.md) |
| `implement-spec` | Implements an entire spec using autonomous subagent task graphs | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/implement-spec/SKILL.md) |
| `surgical-patch` | Surgical bug fixes at the narrowest responsible layer without scope creep | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/surgical-patch/SKILL.md) |
| `diagnosing-bugs` | Scientific hypothesis testing loop for intermittent bugs and regressions | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/diagnosing-bugs/SKILL.md) |
| `code-review` | Two-axis parallel review checking Standards (Fowler smells) and Spec fidelity | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/code-review/SKILL.md) |
| `safe-refactor` | Restructures code while preserving exact behavior with verification brackets | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/safe-refactor/SKILL.md) |
| `verify-and-stop` | Proves existing work meets acceptance conditions without expanding scope | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/verify-and-stop/SKILL.md) |

</details>

<details>
<summary><b>3. Minimalist Code & Token Conservation (Click to expand)</b></summary>

| Skill | Description | Primary File |
| :--- | :--- | :--- |
| `ponytail` | Enforces the 7-rung minimalist code ladder (YAGNI to one-liners) | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/ponytail/SKILL.md) |
| `ponytail-audit` | Whole-repo audit scanning for dead code, unneeded dependencies, and bloat | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/ponytail-audit/SKILL.md) |
| `ponytail-debt` | Harvests `ponytail:` comments into a prioritized technical debt ledger | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/ponytail-debt/SKILL.md) |
| `ponytail-review` | Code review focused exclusively on eliminating over-engineering | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/ponytail-review/SKILL.md) |
| `caveman` | Ultra-compressed token communication protocol preserving 100% technical accuracy | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/caveman/SKILL.md) |
| `cavecrew` | Subagent delegation protocol with compressed output contracts to save context | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/cavecrew/SKILL.md) |
| `caveman-stats` | Calculates real session token usage, turn count, and token savings | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/caveman-stats/SKILL.md) |
| `caveman-explore` | Read-only repository explorer returning compact path:line citations | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/caveman-explore/SKILL.md) |

</details>

<details>
<summary><b>4. Architecture, Governance & Safety (Click to expand)</b></summary>

| Skill | Description | Primary File |
| :--- | :--- | :--- |
| `git-guardrails` | Sets up PreToolUse hooks to intercept and block destructive git commands | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/git-guardrails/SKILL.md) |
| `handoff` | Checkpoints current conversation into `.scratch/handoff.md` for seamless resumption | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/handoff/SKILL.md) |
| `subagent-handoff` | Hands off conversation state to an autonomous background worker | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/subagent-handoff/SKILL.md) |
| `domain-modeling` | Builds and sharpens domain boundaries, CONTEXT.md, and ADRs | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/domain-modeling/SKILL.md) |
| `triage` | Triages incoming issues and PRs through canonical 5-state lifecycle | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/triage/SKILL.md) |
| `setup-ts-deep-modules` | Configures dependency-cruiser to enforce deep module boundaries | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/setup-ts-deep-modules/SKILL.md) |
| `retro` | Post-session retrospective identifying environment and prompt improvements | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/retro/SKILL.md) |

</details>

---

## 🧠 5-Tier Memory Management

To maintain crisp context without attention degradation or token bloat, AAC partitions memory across five distinct tiers:

```text
┌─────────────────────────────────────────────────────────────┐
│ Tier 1: Ephemeral Working Context (Intra-Session)           │ -> Context window & transcript.jsonl
├─────────────────────────────────────────────────────────────┤
│ Tier 2: Workspace Directives (Cross-Session Deterministic)  │ -> AGENTS.md (<12k chars), .agents/rules/*.md
├─────────────────────────────────────────────────────────────┤
│ Tier 3: Domain & Architectural Knowledge (Living Docs)      │ -> CONTEXT.md, docs/adr/*.md
├─────────────────────────────────────────────────────────────┤
│ Tier 4: Session Bridge Handoff (Inter-Session State)        │ -> .scratch/handoff.md via handoff skill
├─────────────────────────────────────────────────────────────┤
│ Tier 5: External Task Graph (Durable Frontier)              │ -> GitHub / Gitea Issues (to-tickets)
└─────────────────────────────────────────────────────────────┘
```

1. **Intra-Session (Tier 1)**: Ephemeral working context managed via progressive disclosure.
2. **Workspace Directives (Tier 2)**: Core guidelines in `AGENTS.md` and rules in `.agents/rules/` (`trigger: always_on`).
3. **Domain Knowledge (Tier 3)**: Living domain glossary in `CONTEXT.md` and immutable decisions in `docs/adr/`.
4. **Session Bridge (Tier 4)**: Cold-start checkpoint saved to `.scratch/handoff.md` before exit. Rehydrated in new sessions via `@handoff.md`.
5. **Durable Task Graph (Tier 5)**: External source of truth for work items managed via GitHub or Gitea issues.

---

## 🛡️ Lifecycle Hooks & Security

AAC integrates with the native Antigravity lifecycle hook engine configured in `.agents/hooks.json`:

### 1. Git Guardrails (`PreToolUse`)
Blocks destructive git commands before `run_command` executes:

```bash
# Cross-platform Node.js hook (Windows, macOS, Linux):
echo '{"toolCall":{"name":"run_command","args":{"CommandLine":"git push origin main"}}}' | node .agents/hooks/block-dangerous-git.cjs
# Output: {"decision":"deny","reason":"BLOCKED: 'git push origin main' matches dangerous git pattern '\\bgit\\s+push\\b'..."}
```

### 2. Quality Gate (`Stop`)
Prevents terminating an agent session if automated tests fail:

```json
{
  "quality-gate": {
    "enabled": true,
    "Stop": [
      {
        "type": "command",
        "command": "node hooks/verify-on-stop.cjs",
        "timeout": 15
      }
    ]
  }
}
```

---

## 🔌 Model Context Protocol (MCP)

AAC natively supports workspace-scoped MCP servers with credential sandboxing.

Copy `.agents/mcp_config.example.json` to `.agents/mcp_config.json` (gitignored):

```bash
cp .agents/mcp_config.example.json .agents/mcp_config.json
```

Configure local Gitea (stdio) and remote GitHub (SSE) connections:

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

---

## 🧪 Verification & Testing

Every commit and installer is validated against a comprehensive automated test suite:

```bash
npm test
```

```text
✔ frontmatter has valid Antigravity name and description
✔ description specifies what it does and when to invoke
✔ body specifies Antigravity research subagent and native tools
✔ artifact carries no placeholder markers
✔ CLI --version prints v5.0.1
✔ CLI --help prints usage banner
✔ CLI list displays skills count
✔ CLI doctor performs environment health checks
✔ CLI init never creates or overwrites package.json in target directory
✔ AGENTS.md remains strictly below 12000 characters limit
✔ memory-management rule exists with trigger: always_on
✔ CONTEXT.md living domain document exists at root
✔ ADR 0001 records 5-tier memory decision
✔ docs/agents configuration files exist and are populated
✔ gitignore correctly ignores .scratch contents and preserves .gitkeep
✔ session handoff template exists
✔ all 64 skills comply with Antigravity operational criteria
ℹ pass 17, fail 0, duration_ms 443
```

---

## 📜 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for more information.

Developed by **Muhammad Rafael Ghifari** ([@rafaelghif](https://github.com/rafaelghif)) for the [Google Antigravity Ecosystem](https://antigravity.google).
