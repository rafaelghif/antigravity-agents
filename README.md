<div align="center">
  <h1>🚀 Antigravity Agent Core (AAC)</h1>
  <p><strong>A Production-Grade Agentic Orchestration Framework</strong></p>

  [![Version](https://img.shields.io/badge/version-4.4.44-blue.svg?style=flat-square)](https://github.com/rafaelghif/antigravity-agents/releases/tag/v4.4.44)
  [![Platform](https://img.shields.io/badge/platform-Antigravity_CLI-8A2BE2.svg?style=flat-square)](https://antigravity.google/docs/cli/overview)
  [![License](https://img.shields.io/badge/license-MIT-green.svg?style=flat-square)](LICENSE)
</div>

---

**Antigravity Agent Core (AAC)** is an advanced orchestration framework designed to elevate standard LLM assistants into robust, multi-agent systems. Built for modern software engineering, AAC emphasizes deterministic workflows, structured intent, and rigorous code verification.

AAC replaces ambiguous "vibe coding" with **Specification-Driven Development**, ensuring that AI agents adhere to strict enterprise guardrails before modifying production codebases.

## 🔥 Key Capabilities

- **Orchestrated Multi-Agent Inbox**: AAC utilizes specialized subagents (`planner`, `implementer`, `reviewer`, `security-reviewer`) that communicate asynchronously via an Inbox. Code modifications require agent consensus before being proposed to the user.
- **Specification-Driven Intent**: Banning vague natural language prompts, AAC mandates machine-readable YAML/Markdown specifications compiled via `scripts/intent_compiler.py` to ensure deterministic execution.
- **Model Context Protocol (MCP) Integration**: Out-of-the-box support for MCP allows agents to securely and standardizedly interface with external databases (Postgres, MySQL) and local toolchains without writing custom connection scripts.
- **Continuous Code Verification**: Integrated with `scripts/verify.py` and GitHub Actions, AAC enforces an Agentic CI/CD loop. If an agent writes code that fails testing, it enters a self-correction loop or autonomously rolls back the state via `git reset`.
- **GitOps Auditing & Telemetry**: Every agent action, thought trajectory, and terminal command is recorded in `.agents/inbox/audit.log` for full observability.
- **Harness Governance**: Strict compute thresholds and rule sets defined in `.agents/harness/guardrails.yml` prevent infinite loops and unauthorized infrastructure modifications.

## 🚀 Installation

Run the reproducible installer to inject the AAC Control Plane into your existing repository.

### Linux / macOS / WSL
```bash
curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/v4.4.44/install.sh | bash
```

### Windows PowerShell
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; iwr -useb https://raw.githubusercontent.com/rafaelghif/antigravity-agents/v4.4.44/install.ps1 | iex
```

> **Note**: Configure your external tool connections by copying `.agents/mcp_config.json.example` to `.agents/mcp_config.json` and injecting your environment variables.

## 🏗️ Core Architecture

AAC extends the native Antigravity environment with structural guardrails:

- 📜 `AGENTS.md` — The centralized Control Plane enforcing BDI (Belief-Desire-Intention) protocols and development standards.
- 📬 `scripts/inbox_manager.py` — The multi-agent message broker and consensus verifier.
- ⚙️ `.agents/harness/` — Governance layer for compute limits and execution guardrails.
- 🧩 `.agents/agents/` — Configuration for autonomous expert subagents.
- 🧠 `.agents/brain/` — Procedural memory enabling agents to persist context and learned rules across sessions.

## 📚 Official Documentation

Explore the official Antigravity documentation to understand the native mechanics powering AAC:
- [Best Practices](https://antigravity.google/docs/cli/best-practices)
- [Plugins and Skills](https://antigravity.google/docs/cli/plugins)
- [Subagents](https://antigravity.google/docs/cli/subagents)
- [Model Context Protocol (MCP)](https://antigravity.google/docs/cli/mcp)

---
<div align="center">
  <sub>Engineered for reliable, scalable AI software development.</sub>
</div>
