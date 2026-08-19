<div align="center">
  <h1>🚀 Antigravity Agent Core (AAC)</h1>
  <p><strong>Stop chatting with AI. Start orchestrating an L9 Principal Engineer.</strong></p>

  [![Version](https://img.shields.io/badge/version-4.4.31-blue.svg?style=flat-square)](https://github.com/rafaelghif/antigravity-agents/releases/tag/v4.4.31)
  [![Platform](https://img.shields.io/badge/platform-Antigravity_CLI-8A2BE2.svg?style=flat-square)](https://antigravity.google/docs/cli/overview)
  [![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)
</div>

---

**Antigravity Agent Core (AAC)** transforms your standard Antigravity workspace from a basic "chat-and-wait" assistant into a **Production-Grade Enterprise Orchestrator**. 

Built for 2026, AAC replaces outdated prompt engineering with rigid **Context Engineering**. It strips away AI hallucinations, enforces Zero Trust security, and runs a synchronized Multi-Agent Pub-Sub Room (Bot Mode) to debate, review, and auto-heal your code until it meets L9 Staff-level standards. 

## 🔥 Why Use AAC? (The L9 Difference)

- **🔄 Multi-Agent Inbox (Bot Mode)**: Stop babysitting. AAC delegates complex tasks to a decentralized team of `planner`, `implementer`, and `reviewer` subagents. They debate asynchronously in a controlled Inbox, verify code, and only bother you when the feature is 100% complete.
- **🛡️ The Control Plane**: Features hardcoded limits against infinite loops, strictly mandates the `Pro` model tier for reasoning tasks, and forbids database schema coupling via Domain-Driven Design (DDD).
- **🧠 Permanent Procedural Memory**: If the agent makes a mistake, it learns from it and writes the fix directly into its physical `.agents/brain/rules.md`. The AI actually gets smarter the longer it stays in your repo.
- **⚡ Anti-Dummy & Boilerplate Ban**: AAC is strictly forbidden from writing `// TODO` stubs, mock arrays, or raw CSS hacks. It mandates framework-native CLIs (`nest g`, `npx shadcn-ui add`), HashMaps over O(N^2) loops, and production-ready implementations.
- **🛡️ Stack-Aware Auto-Healing**: After any code edit, it triggers `scripts/verify.py`. If tests fail, it self-corrects. If it fails consecutively, it automatically executes `git reset --hard HEAD` to prevent piling hacks on top of broken states.

## 🚀 One-Command Bootstrap

Run the reproducible installer to inject the AAC Control Plane into your existing repository. It safely copies policies, verifies hooks, and automatically backs up any existing states.

### Linux / macOS / WSL
```bash
curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/v4.4.31/install.sh | bash
```

### Windows PowerShell
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; iwr -useb https://raw.githubusercontent.com/rafaelghif/antigravity-agents/v4.4.31/install.ps1 | iex
```

> **Note**: Don't forget to configure your databases! Copy `.agents/mcp_config.json.example` to `.agents/mcp_config.json` and inject your `.env` variables to instantly hook up Postgres, MySQL, or MSSQL to the AI.

## 🏗️ The AAC Architecture

AAC leverages standard Antigravity customization paths, but pushes them to the absolute limit:

- 📜 `AGENTS.md` — The L9 Control Plane enforcing Zero-Tolerance standards.
- 📬 `scripts/inbox_manager.py` — The Orchestration Layer for multi-agent asynchronous debates.
- 🧩 `.agents/agents/` — Autonomous experts (`planner`, `implementer`, `reviewer`, `security-reviewer`).
- 🛠️ `.agents/skills/` — On-demand enterprise constraints (`architecture`, `code-quality`, `design`, `security`, `verification`, `mcp-setup`).
- 🧠 `.agents/brain/` — Evolving physical memory.
- ⚙️ `.agents/mcp_config.json` — Out-of-the-box Model Context Protocol integrations.

## 📚 Official Documentation

Explore the official Antigravity documentation to understand the native mechanics powering AAC:
- [Best Practices](https://antigravity.google/docs/cli/best-practices)
- [Plugins and Skills](https://antigravity.google/docs/cli/plugins)
- [Subagents](https://antigravity.google/docs/cli/subagents)
- [Model Context Protocol (MCP)](https://antigravity.google/docs/cli/mcp)

---
<div align="center">
  <sub>Engineered by Anti-Yes-Men for the Antigravity Engine.</sub>
</div>
