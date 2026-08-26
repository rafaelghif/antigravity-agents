<div align="center">
  <h1>🚀 Antigravity Agent Core (AAC)</h1>
  <p><strong>The Enterprise-Grade Agentic Engineering Framework for Google Antigravity</strong></p>

  [![Version](https://img.shields.io/badge/version-4.25.0-blue.svg?style=flat-square)](https://github.com/rafaelghif/antigravity-agents/releases/tag/v4.25.0)
  [![Platform](https://img.shields.io/badge/platform-Antigravity_CLI-8A2BE2.svg?style=flat-square)](https://antigravity.google/docs/cli/overview)
  [![Gates](https://img.shields.io/badge/gates-6%2F6_AST_%26_Test_Passed-brightgreen.svg?style=flat-square)](#-the-6-hard-technical-gates)
  [![MCP](https://img.shields.io/badge/MCP-Ready-orange.svg?style=flat-square)](https://modelcontextprotocol.io/)
  [![Sponsor](https://img.shields.io/badge/sponsor-support-ff69b4.svg?style=flat-square)](#-support--sponsorship)
  [![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)
</div>

---

**Antigravity Agent Core (AAC)** elevates Google Antigravity AI coding assistants into an autonomous, senior-level software engineering unit. While standard AI models produce superficial "vibe coding" — shallow implementations, duplicate code, fake tests, and uncleaned scratch scripts — AAC enforces **System-2 Test-Time Compute (TTC)**, **Deterministic Flow Engineering**, and **Strict Static AST Verification Gates**.

AAC turns your AI into an engineer that thinks before acting, reuses existing code, tests behavioral outcomes, adheres to WCAG 2.2 AA accessibility, and leaves zero garbage in your repository.

---

## 🏗️ Architecture & Execution Flow

AAC operates as a deterministic State Machine, coordinating specialized subagents through an asynchronous inbox and strict verification pipeline:

```mermaid
flowchart TD
    User([👤 User Prompt / Task]) --> PreHook[⚡ Pre-Invoke Hook<br/>Auto-Inject Memory & Relevant Skills]
    PreHook --> Router{CLAS Router}
    
    subgraph MultiAgent [🤖 Multi-Agent Inbox & Consensus]
        Router --> Planner[🎯 Planner Subagent<br/>Architectural Blueprint & DAG Tasks]
        Planner --> Implementer[💻 Implementer Subagent<br/>Minimal Delta & Mandatory TDD]
        Implementer <--> Reviewer[🔍 Peer Reviewer & Security Architect<br/>Diff Audit & Vulnerability Check]
    end

    Reviewer --> VerifyEngine{🛡️ AAC Verification Engine<br/>scripts/verify.py}

    subgraph Gates [🔒 6 Hard Technical Gates]
        VerifyEngine --> G1[1. Anti-Sham Test Quality Guard]
        VerifyEngine --> G2[2. Native DRY Clone Detector]
        VerifyEngine --> G3[3. L9 AST Complexity Analyzer]
        VerifyEngine --> G4[4. Git Hygiene & Scratch Purger]
        VerifyEngine --> G5[5. Graphify Knowledge Graph]
        VerifyEngine --> G6[6. UI Hygiene & WCAG 2.2 AA Guard]
    end

    G1 & G2 & G3 & G4 & G5 & G6 --> GateCheck{All Passed?}
    GateCheck -- ❌ Failed --> AutoFix[🔄 Auto-Remediation Loop<br/>Lateral Thinking & Root Cause Fix]
    AutoFix --> Implementer
    GateCheck -- ✅ Passed --> GitCommit[📦 Clean Conventional Commit<br/>AITL Verified & Zero Scratch Files]
    GitCommit --> Done([🚀 Verified PR / Production Ready])
```

---

## 🔒 The 6 Hard Technical Gates

Unlike generic prompt templates, AAC ships with **native, zero-dependency Python tools** that physically inspect and block substandard code before it enters Git:

| Gate | Tool | What It Enforces |
| :--- | :--- | :--- |
| **1. Anti-Sham Test Guard** | [`scripts/test_quality_guard.py`](scripts/test_quality_guard.py) | **Blocks tautological/fake unit tests.** Inspects AST to reject tests that only assert `callable(fn)`, `hasattr(mod, fn)`, `is not None`, or `expect(fn).toBeDefined()`. Mandates testing real inputs, outputs, exceptions, and edge cases. |
| **2. Native DRY Clone Detector** | [`scripts/dry_guard.py`](scripts/dry_guard.py) | **Blocks code duplication.** Uses normalized rolling-window SHA-256 hashing to find cross-file copy-paste blocks ($\ge 6$ lines) and demands extraction into shared hooks/helpers. |
| **3. L9 AST Complexity Analyzer** | [`scripts/complexity_analyzer.py`](scripts/complexity_analyzer.py) | **Enforces $O(N)$ efficiency.** Forbids nested loops ($O(N^2)$), empty `except: pass` blocks, missing type annotations, and unhandled anti-patterns at the AST level. |
| **4. Git Hygiene & Scratch Purger** | [`scripts/git_hygiene_guard.py`](scripts/git_hygiene_guard.py) | **Eliminates Git garbage.** Intercepts `git commit` to block temporary files (`scratch_*.py`, `tmp_*`, `debug_*`, `*.tmp`, `*.bak`). Sweeps and deletes lingering scratch scripts after each turn. |
| **5. Graphify Knowledge Graph** | [`scripts/semantic_grapher.py`](scripts/semantic_grapher.py) | **Prevents broken refactors.** Computes transitive BFS dependency chains, blast-radius impacts, and exports GraphRAG JSON before touching core modules. |
| **6. UI Hygiene & a11y Guard** | [`scripts/ui_hygiene_guard.py`](scripts/ui_hygiene_guard.py) | **WCAG 2.2 AA & DTCG Tokens.** Enforces visible focus rings (bans bare `outline-none`), `alt` text on images, explicit `<button>` types, and eliminates hardcoded hex colors in favor of design tokens. Inspired by `plugin87/ux-ui-agent-skills`. |

---

## ⚡ Real-World Capabilities

### 🎨 Senior UX/UI Design Architecture (DTCG + WCAG 2.2 AA)
Inspired by best practices from `ux-ui-agent-skills`, AAC equips agents with:
- **3-Tier Design Tokens**: Strict separation of Primitive scales, Semantic intent tokens, and Component-scoped tokens. Zero hardcoded hex colors.
- **Accessible Interactions**: Enforces visible focus rings (`focus-visible:ring-2`), minimum $44\text{px}$ touch targets, screen-reader semantics, and `prefers-reduced-motion` fallbacks.
- **Complete 6-State Spectrum**: Every interactive component must define Default, Hover, Active, Focus-Visible, Disabled, and Async (Loading Skeleton / Empty State) states.
- **Anti-AI-Slop Visual Taste**: Banning generic purple gradients, lack of visual hierarchy, and illegible gray-on-dark contrast.

### 🔌 Model Context Protocol (MCP) Integration
AAC provides first-class configuration templates for MCP servers (`.agents/mcp_config.json.example`). Your agent can securely interact with:
- **Relational Databases**: PostgreSQL, MySQL via native MCP protocol.
- **Browser & E2E Testing**: Headless automation via Puppeteer / Playwright.
- **External Tools**: GitHub Copilot MCP, custom CLI tools, and secure APIs without writing boilerplate connectors.

### 💻 Native Git CLI & AITL Consensus
- **Conventional Commits**: Automates clean, standardized commit history (`feat(...)`, `fix(...)`, `refactor(...)`).
- **AITL (Agent-In-The-Loop) Production Gate**: Destructive actions (`git push`, `npm publish`) require verified consensus from peer review subagents recorded in `.agents/brain/AITL_CONSENSUS.yaml`.

### 🧠 Zero-Amnesia Cross-Session Memory
- **Persistent Context**: Automatically discovers stack dependencies (Next.js, Prisma, Tailwind, Python, Go, etc.) and stores preferences in [`.agents/brain/memory.md`](.agents/brain/memory.md).
- **Self-Learned Rules**: Adapts to project constraints and logs critical lessons into [`.agents/brain/rules.md`](.agents/brain/rules.md) so the agent never repeats past mistakes.

### 🎯 Dynamic Skill Auto-Injection
Context window bloat is eliminated. AAC monitors conversational intent in real-time and injects only the relevant skill instructions (`design`, `architecture`, `security`, `dry`, `code-quality`, `verification`) on-the-fly via [`scripts/hooks/pre_invoke_master.py`](scripts/hooks/pre_invoke_master.py).

---

## 🚀 Quick Start & Installation

Install the AAC Control Plane into any new or existing workspace with a single command:

### Linux / macOS / WSL
```bash
curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/install.sh | bash
```

### Windows (PowerShell)
```powershell
irm https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/install.ps1 | iex
```

> **Zero Destruction Guarantee**: The installer creates an automated timestamped backup in `.agents-backups/` and preserves your existing `.env`, source code, and configurations.

---

## 🔄 Effortless 1-Command Upgrader

Keep your agent framework permanently up-to-date with upstream capabilities:

### Option A: From Terminal
```bash
# Check if a new version is available
python3 scripts/upgrade.py --check

# Upgrade to latest release in 3 seconds (preserves all memory & rules)
python3 scripts/upgrade.py
```

### Option B: Directly in Antigravity Chat
Simply type in the chat prompt:
```text
/upgrade
```
*or ask the agent: "upgrade agent"* — The agent will autonomously check GitHub Releases, apply the latest update, run validation, and report the new features.

---

## 🛠️ Developer Commands Cheat Sheet

| Task | Command | Description |
| :--- | :--- | :--- |
| **Verify Everything** | `python3 scripts/verify.py --execute` | Runs the full verification pipeline (Structural, AST, Anti-Sham, DRY, Git Hygiene, UI a11y). |
| **Check Upgrades** | `python3 scripts/upgrade.py --check` | Queries GitHub Releases to see if a newer AAC version exists. |
| **Perform Upgrade** | `python3 scripts/upgrade.py` | One-click upgrade that preserves user memory and rules. |
| **Audit Duplication** | `python3 scripts/dry_guard.py --check` | Detects cross-file code clones with line numbers and recommendations. |
| **Audit UI & a11y** | `python3 scripts/ui_hygiene_guard.py --check` | Scans JSX/TSX/Vue/Svelte for WCAG 2.2 AA accessibility and design token violations. |
| **Autonomous Learner** | `python3 scripts/self_learner.py "<rule>"` | Persists technical mandates and preferences into procedural memory without duplicates. |
| **Purge Scratch Files** | `python3 scripts/git_hygiene_guard.py --clean` | Sweeps and removes untracked scratch/temporary scripts. |
| **Blast Radius Analysis** | `python3 scripts/semantic_grapher.py --blast-radius <symbol>` | Analyzes all upstream callers impacted by modifying a class/function. |
| **PageRank Centrality** | `python3 scripts/semantic_grapher.py --pagerank` | Computes PageRank centrality to identify core architectural hubs. |
| **Export GraphRAG** | `python3 scripts/semantic_grapher.py --json` | Generates deterministic Knowledge Graph JSON for AST analysis. |
| **Synthesize Skill** | `python3 scripts/self_learner.py --synthesize-skill <name>` | Synthesizes a new custom skill for the workspace on-the-fly. |
| **Terse ACI Verify** | `python3 scripts/verify.py --execute --terse` | Runs all 6 verification gates quietly with a high-density 1-line summary. |

---

## 📁 Repository Structure

```text
├── .agents/
│   ├── agents/          # Specialized subagent definitions (planner, implementer, reviewer, etc.)
│   ├── brain/           # Permanent cross-session memory (memory.md, rules.md, ANCHOR.md)
│   ├── harness/         # Token governance & compute guardrails
│   ├── skills/          # Domain-specific procedures (architecture, caveman, dry, security, design, etc.)
│   └── config.json      # Core framework configuration & version profile
├── scripts/
│   ├── hooks/           # Antigravity lifecycle hooks (pre-invoke context, post-invoke telemetry)
│   ├── complexity_analyzer.py # Enterprise AST & Big-O analyzer
│   ├── dry_guard.py           # Native sliding-window clone detector
│   ├── git_hygiene_guard.py   # Scratch file cleaner & commit blocker
│   ├── self_learner.py        # Autonomous continuous learner across turns
│   ├── semantic_grapher.py    # GraphRAG knowledge graph & blast radius engine
│   ├── test_quality_guard.py  # Anti-sham behavioral test quality guard
│   ├── ui_hygiene_guard.py    # WCAG 2.2 AA accessibility & design token guard
│   ├── upgrade.py             # 1-command effortless upgrader
│   ├── validate.py            # Structural framework validator
│   └── verify.py              # Central verification runner
├── AGENTS.md            # The master policy & World-Class Gates constitution
└── install.sh / install.ps1   # Universal auto-resolving installers
```

---

## 📚 Standing on the Shoulders of Giants (References & Acknowledgments)

AAC synthesizes battle-tested architectural patterns and token-optimization paradigms from open-source pioneers in the AI agent and developer experience ecosystem. Deep gratitude to:

| Project & Author | Core Inspiration in AAC | Impact |
| :--- | :--- | :--- |
| **[JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman)** by Julius Brussee | **Caveman Token Compression Protocol** | Enforces *"Mouth smaller, not brain smaller"*. Strips conversational fluff and pleasantries to cut output tokens by 60%+ while keeping code and commands 100% byte-exact. |
| **[DietrichGebert/ponytail](https://github.com/DietrichGebert/ponytail)** by Dietrich Gebert | **Senior Ladder & Lazy Developer Philosophy** | "Best code is the code you never wrote." Enforces the 7-step decision ladder (YAGNI -> Codebase Reuse -> Stdlib -> Native Platform -> Existing Deps -> 1-Line -> Minimal Diff) preventing over-engineering. |
| **[Graphify-Labs/graphify](https://github.com/Graphify-Labs/graphify)** by Graphify Labs | **AST Knowledge Graph & Blast-Radius Engine** | Direct architectural inspiration for [`scripts/semantic_grapher.py`](scripts/semantic_grapher.py), enabling transitive caller resolution, blast radius calculation, and GraphRAG dependency extraction. |
| **[plugin87/ux-ui-agent-skills](https://github.com/plugin87/ux-ui-agent-skills)** by plugin87 | **Senior UX/UI Design & WCAG 2.2 AA Hygiene** | Foundation for `.agents/skills/design/SKILL.md` and [`scripts/ui_hygiene_guard.py`](scripts/ui_hygiene_guard.py), providing 3-tier DTCG tokens, 6-state interactive spectrums, and visible focus ring linters. |
| **[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)** by Addy Osmani | **Production Webperf & Code-Simplification** | Foundation for `.agents/skills/performance-optimization/` and `.agents/skills/code-simplification/`, bringing Core Web Vitals (LCP, INP, CLS), metric honesty, bundle tree-shaking, and anti-overengineering to AAC. |
| **[obra/superpowers](https://github.com/obra/superpowers)** by Jesse Vincent | **Systematic TDD & Disciplined Agent Pipeline** | Core foundation for AAC's Flow Engineering (`[DRAFT]->[VERIFY]->[FIX]->[FINALIZE]`), strict behavioral TDD enforcement ([`scripts/test_quality_guard.py`](scripts/test_quality_guard.py)), and zero-guesswork root-cause debugging. |
| **[princeton-nlp/SWE-agent](https://github.com/princeton-nlp/SWE-agent)** by Princeton NLP | **Agent-Computer Interface (ACI)** | Model-centric tool feedback (`scripts/verify.py --terse`), precise StartLine/EndLine AST views, and eliminating human terminal noise from LLM context. |
| **[Aider-AI/aider](https://github.com/Aider-AI/aider)** by Paul Gauthier | **Architect/Editor Split & PageRank AST Centrality** | PageRank-weighted centrality ranking in [`scripts/semantic_grapher.py`](scripts/semantic_grapher.py) and separation of architectural planning from line diff editing. |
| **[RooVetGit/Roo-Code](https://github.com/RooVetGit/Roo-Code)** by Roo Code Team | **Scoped Custom Modes & Tool Boundaries** | Specialized subagent definitions with isolated tool permissions (`.agents/agents/`) to eliminate prompt confusion. |
| **[daymade/claude-code-skills](https://github.com/daymade/claude-code-skills)** by daymade | **Dynamic Custom Skill Synthesis Engine** | Autonomous on-demand skill generation in [`scripts/self_learner.py`](scripts/self_learner.py) to automatically create domain-specific skills for user repos. |

---

## 💖 Support & Sponsorship

If Antigravity Agent Core (AAC) saves you hours of debugging, cleans up your AI code, or elevates your development workflow, please consider sponsoring or buying a coffee to support ongoing maintenance and autonomous agent research:

<div align="center">
  <a href="https://github.com/sponsors/rafaelghif"><img src="https://img.shields.io/badge/GitHub_Sponsors-EA4AAA?style=for-the-badge&logo=githubsponsors&logoColor=white" alt="GitHub Sponsors"/></a>
  &nbsp;
  <a href="https://trakteer.id/rafael_ghifari"><img src="https://img.shields.io/badge/Trakteer-c7254e?style=for-the-badge&logo=trakteer&logoColor=white" alt="Trakteer"/></a>
  &nbsp;
  <a href="https://saweria.co/rafaelghifari"><img src="https://img.shields.io/badge/Saweria-FFA500?style=for-the-badge&logo=saweria&logoColor=white" alt="Saweria"/></a>
</div>

---

<div align="center">
  <sub>Built for engineers who demand OP code quality, strict static guarantees, and zero AI fluff.</sub>
</div>
