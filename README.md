# Antigravity Agent Core (AAC) 🚀

> **A project-agnostic operational configuration and workspace blueprint designed for AI software engineering agents (Gemini, Claude, GPT-4). It enforces clean development boundaries, guarantees token-efficiency (prompt caching), and keeps your workspace safe and secure.**
>
> Created by: **Muhammad Rafael Ghifari**  
> Contact Business: [business.rafaelghifari@gmail.com](mailto:business.rafaelghifari@gmail.com)  
> LinkedIn: [rafaelghifari](https://www.linkedin.com/in/rafaelghifari/)  
> GitHub Profile: [rafaelghif](https://github.com/rafaelghif)  
> Project Repository: [antigravity-agents](https://github.com/rafaelghif/antigravity-agents)

---

## 📖 Table of Contents
1. [Overview](#-overview)
2. [How it Works](#-how-it-works)
3. [Step-by-Step Setup Guide](#-step-by-step-setup-guide)
   - [Scenario A: Starting a Brand New / Empty Project](#scenario-a-starting-a-brand-new--empty-project)
   - [Scenario B: Integrating into an Existing Project](#scenario-b-integrating-into-an-existing-project)
4. [Helper Commands Reference (`helper.sh`)](#-helper-commands-reference-helpersh)
5. [The AI Agent's Development Loop](#-the-ai-agents-development-loop)
6. [Core Rules & Architecture Purity](#-core-rules--architecture-purity)

---

## 🌟 Overview

Antigravity Agent Core is a plug-and-play workspace configuration script. When you run the `bootstrap.sh` script in any folder, it automatically constructs a standardized environment with:
- **Global Agent Protocol (`AGENTS.md`)**: Set of instructions that align the AI agent on how to work.
- **Diagnostics & Validator Scripts**: Protects your codebase from hardcoded passwords/credentials, prevents memory/context size bloat, and verifies code isolation patterns.
- **Git Hooks**: Automatically keeps the agent's task checklist and branch status synchronized on every commit.

---

## 🛠️ How it Works

1. You put **only** the `bootstrap.sh` file at the root of your project directory and execute it.
2. The script initializes Git (if not present), scaffolds all required files and scripts inside `.agents/` directory, installs the git hooks, and sets up `AGENTS.md`.
3. It copies itself to `.agents/bootstrap.sh` as a backup.
4. It **automatically deletes itself** from the root, keeping your project directory completely clean!

---

## 🚀 Step-by-Step Setup Guide

No matter if you are an expert developer or have zero coding experience, setting up Antigravity is as easy as running a single command.

### Scenario A: Starting a Brand New / Empty Project

Follow these steps if you are starting a project from a completely empty folder:

#### **Step 1: Open Terminal and Go to Your Folder**
Create a new folder for your project, open your terminal (command prompt), and navigate to it:
```bash
mkdir my-brand-new-project
cd my-brand-new-project
```

#### **Step 2: Run the Bootstrapper**
Run this one-liner command to download and run the bootstrapper:
```bash
curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/bootstrap.sh | bash
```
*(Alternatively, if you cloned the repo locally, run: `/path/to/antigravity-agents/bootstrap.sh`)*

> [!NOTE]
> The script will automatically initialize Git for you and clean itself up when done.

#### **Step 3: Run the Initialization Wizard**
Configure your project details (scaffolding directories and template config files) by running the wizard:
```bash
./.agents/scripts/helper.sh init
```
The wizard will interactively ask you:
1. **Project Name**
2. **Language/Stack** (Node/TypeScript, Go, Python, etc.)
3. **Architecture** (MVC, Clean, Hexagonal)
4. **Database/ORM** (Prisma, PostgreSQL, None)
5. **Environment Variables** (like `PORT`, `DATABASE_URL`)

It will generate the folder structures and config templates instantly. You are now ready to let your AI agent code!

---

### Scenario B: Integrating into an Existing Project

Follow these steps if you already have a codebase and want to add Antigravity:

#### **Step 1: Navigate to Your Project Root**
Open your terminal and go to your existing project folder:
```bash
cd /path/to/your/existing-project
```

#### **Step 2: Run the Bootstrapper**
Execute the script to configure the workspace around your current code:
```bash
curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/bootstrap.sh | bash
```
The script will autodetect your programming language, linter, tests, and database migrations, and write the project settings to `.agents/project_rules.md` automatically!

#### **Step 3: Run diagnostics**
Verify that your existing workspace passes the agent safety checks:
```bash
./.agents/scripts/helper.sh doctor
```
If everything is healthy, commit the configurations to Git:
```bash
git add AGENTS.md .agents/
./.agents/scripts/helper.sh commit chore core "initialize antigravity agent workspace"
```

---

## 💻 Helper Commands Reference (`helper.sh`)

Once bootstrapped, all operations are managed through `./.agents/scripts/helper.sh`. Here is a quick reference:

| Command | Usage | Description |
|---|---|---|
| `init` | `./.agents/scripts/helper.sh init` | Launches the interactive wizard to scaffold folders, configurations, and templates. |
| `recon` | `./.agents/scripts/helper.sh recon` | Re-scans the repository to map directory boundaries, stacks, linters, tests, and API routes. |
| `validate` | `./.agents/scripts/helper.sh validate` | Audits the project for hardcoded credentials/secrets, memory file size limits, and raw process env access. |
| `doctor` | `./.agents/scripts/helper.sh doctor` | Performs diagnostics on git initialization, hook executable permissions, and active locks. |
| `commit` | `./.agents/scripts/helper.sh commit [type] [scope] [desc] [files...]` | Runs validation and tests, then commits changes using the Conventional Commits format (e.g. `feat(auth): add google login`). Use `--no-verify` or `--no-test` to bypass checks. |
| `lock` | `./.agents/scripts/helper.sh lock <module>` | Locks a specific module to prevent parallel developers or agents from modifying the same files simultaneously. |
| `unlock` | `./.agents/scripts/helper.sh unlock <module>` | Releases the lock on a module. |
| `archive` | `./.agents/scripts/helper.sh archive` | Archives completed sprint checklists from `memory.md` to `.agents/archive/` pre-merge to prevent merge conflicts. |

---

## 🔄 The AI Agent's Development Loop

When an AI Agent starts working on a task, it must strictly follow these steps to ensure clean history and zero bugs:

1. **Verify State**: Verify that the workspace is on the correct branch.
2. **Lock Module**: Acquire the module lock to prevent conflicts:
   ```bash
   ./.agents/scripts/helper.sh lock <module_name>
   ```
3. **Implement Feature**: Modify a single file or write unit tests.
4. **Automated Verification & Local Commit**: Stage, validate, run tests, and commit cleanly in one step:
   ```bash
   ./.agents/scripts/helper.sh commit feat core "add new feature implementation"
   ```
5. **Unlock Module**: Release the lock:
   ```bash
   ./.agents/scripts/helper.sh unlock <module_name>
   ```

---

## 🛡️ Core Rules & Architecture Purity

Antigravity Workspace enforces these key rules on AI agents:
- **No Remote Git operations**: The agent is **forbidden** from running `git pull`, `git push`, `git fetch`, or `git checkout -b` to prevent conflicts. Branch management and pushing to remote repos is handled exclusively by **you** (the user).
- **Hardcoded Secret Scan**: The agent cannot commit if there are passwords, private keys, or API tokens exposed in the codebase (scanned via `validate.sh`).
- **Context Preservation**: Keeps the task checklists small and modular (`memory.md` capped at 100 lines) to achieve 100% prompt cache hits, making agent invocations 80% faster and cheaper.
