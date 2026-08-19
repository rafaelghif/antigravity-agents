<div align="center">
  <h1>🚀 Antigravity Agent Core (AAC)</h1>
  <p><strong>A deterministic, fully autonomous, and self-learning workspace policy for AI coding.</strong></p>

  [![Version](https://img.shields.io/badge/version-4.4.26-blue.svg?style=flat-square)](https://github.com/rafaelghif/antigravity-agents/releases/tag/v4.4.26)
  [![Platform](https://img.shields.io/badge/platform-Antigravity_CLI-8A2BE2.svg?style=flat-square)](https://antigravity.google/docs/cli/overview)
</div>

---

**Antigravity Agent Core (AAC)** transforms your standard Antigravity workspace into an enterprise-grade AI development ecosystem. AAC operates on a strict, hallucination-resistant policy that enforces world-class software engineering practices. Unlike standard "chat-and-wait" assistants, AAC acts as a **Principal Architect**: capable of autonomous orchestration, automated git rollbacks, and persistent self-learning.

## ✨ Key Capabilities

- **🔄 Fully Autonomous Goal-Seeking**: Trigger the `/goal` command to let the agent orchestrate sub-agents (Planner → Implementer → Reviewer), self-heal tests, and iterate tirelessly until the final outcome meets Enterprise standards.
- **🧠 Persistent Self-Learning**: Through the `/learn` command, AAC permanently logs your architectural preferences and bug-fixes into its physical `.agents/brain/rules.md`. It never repeats the same mistake twice.
- **🛡️ Stack-Aware Healing & Rollbacks**: Automatically triggers `scripts/verify.py --execute` after coding. If the tests fail 3 times, the agent automatically executes `git restore . && git clean -fd` to revert to a pristine state.
- **⚡ CLI-First & Boilerplate Ban**: AAC is strictly forbidden from manually typing empty boilerplate. It mandates the use of framework-native generators (`nest g`, `ionic g`, `npx shadcn-ui add`).
- **🎨 Design & UX Mastery**: Dedicated `.agents/skills/design/SKILL.md` ensures mobile-first CSS, standard utility classes (Tailwind), a11y compliance, and mandatory fallback UI states (Loading/Error/Empty).

## 🚀 Quick Start

Run the reproducible installer to bootstrap your current repository. The installer will safely copy managed files, validate schema integrity, and automatically back up existing states.

### Linux / macOS / WSL
```bash
curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/v4.4.26/install.sh | bash
```

### Windows PowerShell
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; iwr -useb https://raw.githubusercontent.com/rafaelghif/antigravity-agents/v4.4.26/install.ps1 | iex
```

> **Note**: Copy `.agents/antigravity-settings.example.json` manually to `~/.gemini/antigravity-cli/settings.json` to adapt global CLI permissions to your environment.

## 🏗️ Core Architecture

AAC is built on the official Antigravity customization principles, maintaining a minimal footprint:

- 📜 `AGENTS.md` — The ultimate source of truth (always-on policy, orchestration, self-learning).
- 🧩 `.agents/agents/` — L9-level expert sub-agents (`planner`, `implementer`, `reviewer`, `security`).
- 🛠️ `.agents/skills/` — On-demand capabilities (`architecture`, `code-quality`, `design`, `security`, `verification`).
- 🧠 `.agents/brain/` — The physical long-term memory for persistence.
- ⚙️ `.agents/mcp_config.json` — Pre-configured Model Context Protocol (MCP) integrations.
- 🔬 `scripts/verify.py` — Dynamic project stack analyzer and verification runner.

## 🔄 The Delivery Protocol

AAC enforces a strict, logical pipeline for every AI interaction. This is not a suggestion—it's the built-in protocol:

1. **Load Skill & Context**: Verify dependencies and architectural constraints (`grep_search` over blind reads).
2. **Plan**: Draft a roadmap via the `planner` subagent.
3. **Execute**: Delegate to `implementer` to write the exact minimal delta.
4. **Verify & Heal**: Trigger `verify.py` to auto-heal. Rollback if broken.
5. **Peer Review**: Await `STATUS: APPROVED` from the `reviewer` subagent.
6. **Atomic Commit**: Stash changes cleanly using Conventional Git Commits.

## 📚 References & Documentation

Explore the official Antigravity documentation to understand the mechanics powering AAC:
- [Best Practices](https://antigravity.google/docs/cli/best-practices)
- [Plugins and Skills](https://antigravity.google/docs/cli/plugins)
- [Subagents](https://antigravity.google/docs/cli/subagents)
- [Model Context Protocol (MCP)](https://antigravity.google/docs/cli/mcp)
- [Permissions and Sandbox](https://antigravity.google/docs/cli/permissions)

---
<div align="center">
  <sub>Built with precision for Gemini and Antigravity CLI.</sub>
</div>
