# Task: Automated Skill Registry Command Implementation

This document logs the design decisions, command interface structures, and execution steps for implementing the **Automated Skill Registry** feature in Antigravity Agent Core (AAC).

---

## 1. Design Decisions

### 1.1 Command Interface in `helper.sh`
*   **`create-skill <name> [description]`**:
    *   Creates a directory at `.agents/skills/<name>/`.
    *   Generates a standardized `.agents/skills/<name>/SKILL.md` with YAML frontmatter.
    *   Creates a placeholder script directory `.agents/skills/<name>/scripts/` and sets up a default executable script template.
*   **`list-skills`**:
    *   Scans `.agents/skills/` directory.
    *   Audits each skill for Keep-a-Skill compliance criteria (YAML frontmatter, no placeholders, valid script execution paths).
    *   Outputs a neat tabulated overview of all registered and compliant skills.

### 1.2 Skill Compliance Verification Rules
A skill is considered compliant if:
1.  `SKILL.md` exists inside the skill directory.
2.  `SKILL.md` starts with a valid, parsed YAML frontmatter containing `name` and `description`.
3.  The file contains no placeholders or generic text (like `TODO`, `FIXME`, or `[placeholder]`).
4.  All referenced scripts under the `scripts/` block exist in the local filesystem and have execution permissions (`chmod +x`).

### 1.3 Agent-Initiated Dynamic Skill Creation (Aligned via `/grill-me`)
When the agent needs a capability that does not exist in the current workspace, it can autonomously create, audit, and commit the skill:
1.  **Trigger**: Contextual Discovery. Initiated when the agent dynamically identifies gaps when trying to perform a complex or repetitive task that doesn't fit standard skills (e.g. repeated patterns > 3 times), or when explicitly requested by the user.
2.  **Implementation**: Fully Programmed. The agent designs the operational rules, writes instructions in `SKILL.md`, and implements active scripts under `scripts/`.
3.  **Scripting Runtime**: Python (.py). Generated scripts will use python3.
4.  **Script Structure**: Structured JSON-ready. Python scripts must utilize `argparse` for CLI arguments, structured `try-except` blocks, logging, and output results in JSON format to stdout for easy parsing.
5.  **Auditing**: The agent validates the created skill using `helper.sh list-skills` and checks execution permissions.
6.  **Error Handling**: Rollback & Auto-Refine. The agent attempts to fix compliance issues or script bugs. If the audit/tests still fail after 2 refinement attempts, it rolls back (deletes the directory) and notifies the user in chat.
7.  **Registration & Tracking**: Auto-discovered by the skill scanner, with the dynamic skill registered/logged in `memory.md` under the active workflow or decision log. No manual modification of global static config files is required.
8.  **Commit Flow**: Completely autonomous. The agent will run `./.agents/scripts/helper.sh commit` to stage, validate, and commit the new skill to Git without interactive user prompts, provided all validation/auditing checks pass.

---

## 2. Implementation Steps

*   [x] **Step 1: Scaffolding templates in `bootstrap.sh`**
    *   Add the default template for `SKILL.md` inside `bootstrap.sh`.
    *   Add default Python script template inside `bootstrap.sh`.
*   [x] **Step 2: Implement `create-skill` inside `helper.sh`**
    *   Create `cmd_create_skill` in `helper.sh` and templates.
    *   Generate folder structure and write `SKILL.md` dynamically.
    *   Support both default Bash template and Python template generation.
    *   Ensure the tool can be invoked programmatically by the agent or manually by the user.
*   [x] **Step 3: Implement `list-skills` and Auditor inside `helper.sh`**
    *   Create `cmd_list_skills` in `helper.sh` and templates.
    *   Write frontmatter and file parsers using grep/sed/awk to ensure zero third-party dependencies.
*   [x] **Step 4: Verification and Testing**
    *   Create a test skill using `helper.sh create-skill`.
    *   Verify auditing logs are correct.
    *   Verify failure logs by injecting a placeholder `TODO` text.
*   [ ] **Step 5: Documentation & Release**
    *   Update README.md and CHANGELOG.md.
    *   Bump version to `1.5.0` using `helper.sh release minor`.
