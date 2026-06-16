# Antigravity Agent Core (AAC) 🚀

<p align="center">
  <a href="https://github.com/rafaelghif/antigravity-agents/blob/main/LICENSE"><img src="https://img.shields.io/github/license/rafaelghif/antigravity-agents?style=flat-square&color=blue" alt="License"></a>
  <a href="https://github.com/rafaelghif/antigravity-agents/pulls"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square" alt="PRs Welcome"></a>
  <a href="https://github.com/rafaelghif/antigravity-agents/stargazers"><img src="https://img.shields.io/github/stars/rafaelghif/antigravity-agents?style=flat-square&color=yellow" alt="Stars"></a>
  <a href="https://github.com/rafaelghif/antigravity-agents/network/members"><img src="https://img.shields.io/github/forks/rafaelghif/antigravity-agents?style=flat-square&color=lightgrey" alt="Forks"></a>
</p>

**Antigravity Agent Core** is a project-agnostic operational workspace layout and developer protocol designed specifically for AI software engineering agents (such as Gemini, Claude, GPT-4, Cursor, Aider, and local LLMs). 

It enforces developer discipline, enables zero-hallucination execution, optimizes token efficiency (reducing API cost and latency by up to 80% through model-side prompt caching), and secures the codebase against hardcoded credentials and boundary leaks.

---

## 🌟 Open Source & Free Forever

This project is **100% Free, Open Source, and Openly Licensed** under the MIT License:
- **Free to Use**: Deploy it in your personal, commercial, or enterprise repositories without any cost.
- **Free to Fork**: Customize the skills, scripts, and rules to match your team's specific developer workflows.
- **Free to Contribute**: Pull requests, issues, and ideas are highly welcome! Help us build the ultimate workspace for AI agents.

---

## ⚠️ Disclaimer & No Warranty (Read Before Use)

> [!CAUTION]
> **ALL USAGE IS ENTIRELY AT YOUR OWN RISK. THIS FRAMEWORK IS PROVIDED "AS IS" WITHOUT ANY WARRANTY OF ANY KIND.**
>
> By using Antigravity Agent Core, you acknowledge and agree to the following:
>
> - **Financial Responsibility (API & Token Costs)**: AI agent operations are highly recursive and can consume a significant volume of LLM tokens (input, output, and caching). You are **solely responsible** for all charges billed by your AI providers.
> - **Operational & Code Risk**: Autonomous agents can modify files, execute terminal scripts, alter directories, and rewrite Git branches. Always execute agent tasks in a safe development workspace.
> - **No Liability**: In no event shall the author or contributors be liable for any direct, indirect, incidental, or consequential damages.
> - **Responsible Review**: You are responsible for inspecting all agent-generated code, commit logs, and validation results before merging them.

---

## 🚀 30-Second Quick Start

Get any local repository agent-ready in a single command.

### 💻 1. Installation

Open your terminal in your project root folder and execute the appropriate command for your operating system:

#### **Linux & macOS (Bash/Zsh)**
```bash
curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/bootstrap.sh | bash
```

#### **Windows (PowerShell)**
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/bootstrap.ps1'))
```

---

### 🩺 2. Verify Workspace Health & Onboarding Tutorial
Run the doctor tool to inspect active hooks, locks, script permissions, and validation checks:
```bash
./.agents/scripts/helper.sh doctor
```
Or view the friendly step-by-step interactive developer guide:
```bash
./.agents/scripts/helper.sh guide
```

---

### 💡 3. Simplified Developer Cheat Sheet (Daily Essentials)

If you are a developer, you only need to know these daily essentials:

- **Interactive Onboarding Tutorial**:
  ```bash
  ./.agents/scripts/helper.sh guide
  ```
- **Lock a Module (Before Editing)**:
  ```bash
  ./.agents/scripts/helper.sh lock <module-name>
  ```
- **Commit Your Code Safely**:
  ```bash
  ./.agents/scripts/helper.sh commit
  ```
- **Manage Local Issues**:
  ```bash
  ./.agents/scripts/helper.sh issue <list/create/view/close>
  ```
  *(Commit descriptions containing `closes #XX` automatically close the issue and stage it)*
- **Verify Compliance Manual Check**:
  ```bash
  ./.agents/scripts/helper.sh validate
  ```

---

## 📖 Detailed Documentation Index

For in-depth guides on the layout, configuration, and advanced commands, refer to the sub-documentations below:

1. 📂 [Directory Structure Blueprint](file://./docs/directory_blueprint.md) — Map of the generated operational structures and workspace components.
2. ⚡ [Core Features & Capabilities](file://./docs/features_capabilities.md) — Initialization wizard, adaptation, monorepo handling, and Docker provisioning.
3. ⚙️ [Step-by-Step Setup Guide](file://./docs/setup_guide.md) — Detailed integration workflows for new and existing projects.
4. 🛠️ [Operational Scripts Guide (helper.sh)](file://./docs/cli_guide.md) — Detailed subcommand documentation, arguments, and PowerShell parameters.
5. 🔄 [Typical Workflow for the Agent](file://./docs/agent_workflow.md) — Step-by-step task loop execution process.
6. 🛡️ [Core Rules & Architecture Purity](file://./docs/rules_architecture.md) — Enforced rules, boundary guidelines, and caching protocols.
7. 🚀 [Migration Guide](file://./docs/migration_guide.md) — How to upgrade older AAC setups to modern standards.
8. 🔑 [API Profile Rotation & Budget Tracking](file://./docs/api_rotation.md) — Multi-platform auto-rotation, PowerShell integration, and token budget limits.
9. 📅 [Agent Core Changelog](file://./CHANGELOG.md) — Log of version releases and update details.
10. 📌 [Architectural Decision Records (ADRs)](file://./.agents/adr.md) — Historical architectural decisions ledger.

---

## 👤 Created By & Contact

This project is created and maintained with 💙 by:

- **Author**: Muhammad Rafael Ghifari
- **Business Email**: [business.rafaelghifari@gmail.com](mailto:business.rafaelghifari@gmail.com)
- **LinkedIn**: [rafaelghifari](https://www.linkedin.com/in/rafaelghifari/)
- **GitHub**: [rafaelghif](https://github.com/rafaelghif)

Feel free to open an issue or submit a pull request on the [GitHub Repository](https://github.com/rafaelghif/antigravity-agents).
