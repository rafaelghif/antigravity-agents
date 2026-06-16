# Step-by-Step Setup Guide

This guide details how to install and initialize the Antigravity Agent Core workspace configurations in both new and existing repositories.

---

## 1. Prerequisites

Before running the bootstrapper or using the helper CLI, ensure your system meets these prerequisites:
- **Git**: Installed and available in your system `PATH`.
- **Python 3.8+**: Installed and available as `python3` (or `python` on Windows) in your system `PATH`. The framework uses a modular Python engine for subcommands.
- **Git Bash** (Windows only): Required to execute the shell scripts on Windows.

---

## 2. Scenario A: Starting a Brand New / Empty Project

Follow these steps if you are starting a project from a completely empty folder:

### **Step 1: Open Terminal and Go to Your Folder**
Create a new folder for your project, open your terminal (command prompt), and navigate to it:
```bash
mkdir my-brand-new-project
cd my-brand-new-project
```

### **Step 2: Run the Bootstrapper**

#### **For Linux/macOS:**
```bash
# Download and execute
curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/bootstrap.sh | bash

# Or run from local clone
/path/to/antigravity-agents/bootstrap.sh
```

#### **For Windows (PowerShell):**
```powershell
# Download and execute
Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/bootstrap.ps1'))

# Or run from local clone
powershell -ExecutionPolicy Bypass -File \path\to\antigravity-agents\bootstrap.ps1
```

#### **Bootstrapper CLI Options & Flags**
Both `bootstrap.sh` and `bootstrap.ps1` accept command-line arguments to customize their run behavior:

| Linux/macOS Flag | Windows PowerShell Option | Description |
|---|---|---|
| `-f`, `--force` | `-Force` | **Force Overwrite**: Forces the script to overwrite existing files, templates, hooks, and configurations in `.agents/`. (Default: `false`, preserves user changes). |
| `-u`, `--update` | `-Update` | **Update Only**: Performs an update of the core scripts in `.agents/scripts/` to the latest version, without overwriting custom workspace configurations, rules, or the active memory ledger. |
| *N/A* | `-Version <version>` | **Target Version**: (PowerShell wrapper only) Downloads and executes a specific version/branch of the bootstrapper (defaults to `main`). |

> [!NOTE]
> The script will automatically initialize Git for you and clean itself up from the root when done.

### **Step 3: Run the Initialization Wizard**
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

## 3. Scenario B: Integrating into an Existing Project

Follow these steps if you already have a codebase and want to add Antigravity:

### **Step 1: Navigate to Your Project Root**
Open your terminal and go to your existing project folder:
```bash
cd /path/to/your/existing-project
```

### **Step 2: Run the Bootstrapper**

#### **For Linux/macOS:**
```bash
curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/bootstrap.sh | bash
```

#### **For Windows (PowerShell):**
```powershell
Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/bootstrap.ps1'))
```
The script will autodetect your programming language, linter, tests, and database migrations, and write the project settings to `.agents/rules/project_rules.md` automatically!

> [!TIP]
> Just like in Scenario A, you can pass optional CLI flags to the bootstrapper (e.g. `-u` / `-Update` to perform update-only of core scripts, or `-f` / `-Force` to overwrite existing configuration templates).

### **Step 3: Run Diagnostics & Commit**
Verify that your existing workspace passes the agent safety checks:
```bash
./.agents/scripts/helper.sh doctor
```
If everything is healthy, stage the configurations and make your first validated commit:
```bash
git add AGENTS.md .agents/ .antigravityignore
git commit -m "chore(core): initialize antigravity agent workspace"
```
