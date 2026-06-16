# Migration Guide (Upgrading from Older Versions)

This document details how to upgrade existing workspaces configured with older versions of the Antigravity Agent to the latest V1.4.0+ standards.

---

## 1. Automated Upgrade (Recommended)

1. First, pull the latest system files and script templates:

   **For Linux/macOS (Bash/Zsh):**
   ```bash
   curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/bootstrap.sh | bash -s -- --update
   ```

   **For Windows (PowerShell):**
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; iex ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/bootstrap.ps1')); powershell -ExecutionPolicy Bypass -File .\bootstrap.ps1 -Update
   ```

2. Run the automated migration command:
   ```bash
   ./.agents/scripts/helper.sh migrate
   ```
   *This automatically backs up your existing configuration files (`memory.md`, `rules/project_rules.md`, `schema.md`) to `.backup` extensions, updates system hooks and subdirectories, upgrades your active memory schema, and runs auto-recon to align rules.*

---

## 2. Manual Step-by-Step Migration

For full details, precautions, and manual step-by-step migration instructions, refer to the standalone [MIGRATION.md](file://./MIGRATION.md) guide in the project root.
