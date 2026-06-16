# Directory Structure Blueprint

This document outlines the operational directory layout of the Antigravity Agent Core (AAC) workspace setup when initialized in a project.

---

## 1. Directory Structure Mappings

```
[Project Root]
  ├── bootstrap.sh                <-- Bootstrapper entrypoint (automatically deletes itself)
  ├── bootstrap.ps1               <-- Windows Bootstrapper entrypoint (automatically deletes itself)
  ├── AGENTS.md                   <-- Static: Global Agent Protocol (cached)
  ├── README.md                   <-- Static: Developer handbook
  ├── .github/                    <-- GitHub configurations
  │     └── workflows/
  │           └── antigravity.yml <-- CI workspace validator workflow
  └── .agents/                    <-- Workspace operational directory (generated)
        ├── bootstrap.sh          <-- Local backup of the bootstrapper script
        ├── schema.md             <-- Semi-Static: Database & API specs index
        ├── adr.md                <-- Static: Architectural Design Records (cached)
        ├── memory.md             <-- Dynamic: Active task state (<100 lines)
        ├── rules/                <-- Static: Workspace rules including tech stack and architecture
        │     └── project_rules.md <-- Static: Tech Stack, coding rules, & gates (cached)
        ├── schemas/              <-- Semi-Static: Domain-driven schema files (lazy-loaded)
        │     └── default_module.md
        ├── skills/               <-- Static: Generalized parameterizable agent skills
        │     ├── codebase-recon/
        │     ├── git-ops/
        │     ├── test-driven-patch/
        │     ├── infra-provisioner/
        │     ├── security-ci-audit/
        │     └── code-review/
        ├── locks/                <-- Dynamic: Module locks preventing parallel edits
        ├── workflows/            <-- Project-specific implementation plans
        ├── scripts/              <-- Workspace management scripts
        │     ├── helper.sh       <-- Main command dispatcher (thin wrapper forwarding to Python CLI)
        │     ├── helper.ps1      <-- Windows command dispatcher (thin wrapper forwarding to Python CLI)
        │     ├── recon.sh        <-- Auto-reconnaissance scanner
        │     ├── validate.sh     <-- Security and standards validator
        │     └── cli/            <-- Modular Python CLI engine and subcommand modules
        └── archive/              <-- Historical: Completed sprint/checklists archives
```
