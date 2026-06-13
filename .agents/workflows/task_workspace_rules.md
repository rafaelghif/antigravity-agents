# Task: Workspace Rules Registry and Legacy Migration Implementation

This document logs the design decisions, command interfaces, and implementation steps for introducing the **Workspace Rules Registry** and legacy `.agent/rules/` migration in Antigravity Agent Core.

---

## 1. Design Decisions

### 1.1 Directory Structure and Legacy Migration
*   **Directory**: Rules will reside in `.agents/rules/`.
*   **Legacy Folder migration**:
    *   During bootstrap (`bootstrap.sh`) and init/recon, check if the legacy `.agent/rules/` folder exists.
    *   If it exists, automatically migrate (move) any files from `.agent/rules/` to `.agents/rules/`, delete the old empty directory `.agent/rules/`, and log the action.
    *   Record legacy rule migrations in `.agents/memory.md`.

### 1.2 Rule File Structure
Rule files will be written as markdown documents (e.g. `.agents/rules/<name>.md`) with YAML frontmatter:
```markdown
---
name: rule-name
activation: Manual | Always On | Model Decision | Glob
pattern: "src/**/*.ts" # Required if activation is Glob
description: "Natural language description of when to apply the rule." # Required if activation is Model Decision
---

# Rule Title

## Guidelines
- Write guidelines here.
```

### 1.3 Command Interface in `helper.sh`
*   **`create-rule <name> <activation> [description_or_pattern]`**:
    *   Enforces kebab-case for `<name>`.
    *   Enforces `<activation>` to be one of: `manual`, `always-on`, `model-decision`, `glob`.
    *   Generates the `.agents/rules/<name>.md` with correct YAML frontmatter and placeholder body.
*   **`list-rules`**:
    *   Scans `.agents/rules/` and audits each rule for:
        1. Valid file extension (`.md`).
        2. Valid YAML frontmatter containing `name` and `activation`.
        3. Compliance of activation mode parameters (`pattern` for glob, `description` for model-decision).
        4. Absence of placeholders like `TODO`, `FIXME`, or `[placeholder]`.
    *   Outputs a neat tabulated summary of registered rules and their activation modes.

---

## 2. Implementation Steps

*   [ ] **Step 1: Legacy migration logic in `bootstrap.sh` and `helper.sh`**
    *   Implement folder check for `.agent/rules/` in `bootstrap.sh` and `cmd_init` in `helper.sh`.
    *   If found, move files to `.agents/rules/` and cleanup the legacy folder.
*   [ ] **Step 2: Scaffolding rules templates in `bootstrap.sh`**
    *   Ensure the `.agents/rules/` directory is created.
*   [ ] **Step 3: Implement `create-rule` in `helper.sh` and templates**
    *   Add `cmd_create_rule` to `helper.sh` and `bootstrap.sh` templates.
    *   Implement frontmatter generation and parameters validation.
*   [ ] **Step 4: Implement `list-rules` in `helper.sh` and templates**
    *   Add `cmd_list_rules` and `audit_rule` functions.
    *   Parse YAML frontmatter using zero-dependency grep/sed/awk.
*   [ ] **Step 5: Verification & Testing**
    *   Test legacy migration by creating a fake `.agent/rules/` directory and running bootstrap.
    *   Test rule creation and list auditing logic.
*   [ ] **Step 6: Release & Commit**
    *   Update `README.md` and `CHANGELOG.md`.
    *   Set State Flag to `COMPLETED` and commit autonomously.
