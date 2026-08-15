<div align="center">
  <h1>🚀 Antigravity Agent Core (AAC)</h1>
  <p><strong>A deterministic, always-on workspace policy for reliable AI coding.</strong></p>

  [![Version](https://img.shields.io/badge/version-4.4.8-blue.svg?style=flat-square)](https://github.com/rafaelghif/antigravity-agents/releases/tag/v4.4.8)
  [![Platform](https://img.shields.io/badge/platform-Antigravity_CLI-8A2BE2.svg?style=flat-square)](https://antigravity.google/docs/cli/overview)
</div>

---

**Antigravity Agent Core (AAC)** transforms your standard Antigravity workspace into an enterprise-grade AI development environment. It introduces a strict, zero-hallucination execution policy, highly specialized sub-agents, and self-healing verification loops to ensure your AI assistant writes maintainable, secure, and production-ready code.

## ✨ Key Capabilities

- **🧠 Specialized Sub-Agents**: Delegate complex tasks to expert personas including a *Planner*, *Implementer*, *Reviewer*, and *Security Auditor*.
- **🛡️ Stack-Aware Verification**: Automatically detects your project's stack (npm, pnpm, python, etc.) and enforces rigorous pre-commit test healing.
- **⚡ Deterministic Constraints**: The `AGENTS.md` policy strictly limits the AI's blast radius, ensuring it focuses purely on the requested scope without unsolicited refactoring.
- **🔒 Security-First**: Out-of-the-box skills that enforce strict secret-scanning, boundary audits, and safe installer executions.

## 🚀 Quick Start

Run the reproducible installer to bootstrap your current repository. The installer will safely copy managed files, validate schema integrity, and automatically back up existing states.

### Linux / macOS / WSL
```bash
curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/v4.4.8/install.sh | bash
```

### Windows PowerShell
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; iwr -useb https://raw.githubusercontent.com/rafaelghif/antigravity-agents/v4.4.8/install.ps1 | iex
```

> **Note**: Copy `.agents/antigravity-settings.example.json` manually to `~/.gemini/antigravity-cli/settings.json` to adapt global CLI permissions to your environment.

## 🏗️ Core Architecture

AAC is built on the official Antigravity customization principles, maintaining a minimal footprint:

- 📜 `AGENTS.md` — The ultimate source of truth (always-on policy, <600 words).
- 🧩 `.agents/agents/` — L9-level expert sub-agents ready to be invoked.
- 🛠️ `.agents/skills/` — On-demand capabilities (`architecture`, `code-quality`, `security`, `verification`).
- ⚙️ `.agents/mcp_config.json` — Pre-configured Model Context Protocol (MCP) integrations.
- 🔬 `scripts/verify.py` — Dynamic project stack analyzer and verification runner.

## 🔄 The Delivery Protocol

AAC enforces a strict, logical pipeline for every AI interaction. This is not a suggestion—it's the built-in protocol:

1. **Explore**: Comprehensively read dependencies and contracts.
2. **Plan**: Draft a roadmap for multi-file or architectural changes.
3. **Execute**: Implement the exact minimal delta (no speculative changes).
4. **Verify**: Trigger `verify.py` to test and auto-heal any broken code.
5. **Review**: Final human/agent audit of the diff and security boundaries.

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
