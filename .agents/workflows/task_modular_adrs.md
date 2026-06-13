# Task: Modular ADR Scaffolding and Validation

This document tracks the design and implementation steps for modularizing Architectural Decision Records (ADRs) and validating them in the workspace.

---

## 1. Design Decisions

*   Create `.agents/adrs/` folder during initialization/migration/bootstrap.
*   Migrate existing `ADR-001` template to `.agents/adrs/001-initial-workspace-protocol.md`.
*   Rewrite `.agents/adr.md` to be an index map registering all ADR files.
*   Implement `create-adr <title> [status]` in `helper.sh` (which auto-formats number/title and appends to index).
*   Add Check 10 to `validate.sh` validating ADR compliance (index tracking, no placeholders).
*   Package updates inside the main installer templates in `bootstrap.sh`.

---

## 2. Implementation Steps

*   [x] **Step 1: Lock rules and update memory.md**
    *   Lock `rules` module and set the task checklist in `memory.md` to `[/]` (In Progress)
*   [x] **Step 2: Migrate ADR-001 and rewrite adr.md**
    *   Create `.agents/adrs/` folder.
    *   Write `.agents/adrs/001-initial-workspace-protocol.md` with initial protocol adoption context.
    *   Rewrite `.agents/adr.md` to be a clean index mapping to it.
*   [x] **Step 3: Implement `create-adr` subcommand in `helper.sh`**
    *   Add command to `helper.sh` template and help menu.
    *   Support kebab-case file generation and index registration.
*   [x] **Step 4: Implement ADR compliance Check 10 in `validate.sh`**
    *   Add validation loop mapping `.agents/adrs/*.md` to `.agents/adr.md`.
    *   Audit each ADR file for placeholders (`TODO`/`FIXME`/`[placeholder]`).
*   [x] **Step 5: Package changes in `bootstrap.sh` template installer**
    *   Ensure new workspaces automatically create `.agents/adrs/` and bootstrap `001-initial-workspace-protocol.md` and clean index `adr.md`.
*   [x] **Step 6: Run validation and commit changes**
    *   Run `./.agents/scripts/helper.sh validate` and commit successfully.
