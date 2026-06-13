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

---

## 2. Implementation Steps

*   [ ] **Step 1: Scaffolding templates in `bootstrap.sh`**
    *   Add the default template for `SKILL.md` inside `bootstrap.sh`.
    *   Add default script template inside `bootstrap.sh`.
*   [ ] **Step 2: Implement `create-skill` inside `helper.sh`**
    *   Create `cmd_create_skill` in `helper.sh` and templates.
    *   Generate folder structure and write `SKILL.md` dynamically.
*   [ ] **Step 3: Implement `list-skills` and Auditor inside `helper.sh`**
    *   Create `cmd_list_skills` in `helper.sh` and templates.
    *   Write frontmatter and file parsers using grep/sed/awk to ensure zero third-party dependencies.
*   [ ] **Step 4: Verification and Testing**
    *   Create a test skill using `helper.sh create-skill`.
    *   Verify auditing logs are correct.
    *   Verify failure logs by injecting a placeholder `TODO` text.
*   [ ] **Step 5: Documentation & Release**
    *   Update README.md and CHANGELOG.md.
    *   Bump version to `1.5.0` (minor version bump since it's a new feature) using `helper.sh release minor`.
