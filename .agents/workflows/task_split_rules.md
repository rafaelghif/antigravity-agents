# Task: Split Project Rules into Modular Blueprints

This document logs the design decisions and implementation steps for splitting the monolithic `project_rules.md` file into separate, modular rule files under `.agents/rules/`.

---

## 1. Design Decisions

We will split `.agents/rules/project_rules.md` into the following modular files:

### 1.1 `project_rules.md`
*   **Activation**: `Always On`
*   **Focus**: Stack boundaries, directory structure, linter/build/test commands, and multi-agent coordination.

### 1.2 `mvc_conventions.md`
*   **Activation**: `Model Decision`
*   **Description**: "Conventions for standard Model-View-Controller (MVC) architecture and boundary insulation."
*   **Focus**: Architectural conventions, MVC separation, and pure business logic insulation.

### 1.3 `db_rules.md`
*   **Activation**: `Glob`
*   **Pattern**: `src/models/**/*.ts`
*   **Focus**: TypeORM database entities, schemas, and models.

### 1.4 `security_rules.md`
*   **Activation**: `Always On`
*   **Focus**: Required configuration variables, credential scanning, and raw environment access boundaries.

---

## 2. Implementation Steps

*   [x] **Step 1: Acquire module lock and set task to in progress**
    *   Run `./.agents/scripts/helper.sh lock rules`
    *   Set active task checklist in `.agents/memory.md` to `[/]`
*   [x] **Step 2: Create `mvc_conventions.md`, `db_rules.md`, and `security_rules.md`**
    *   Implement each modular rule file with correct YAML frontmatter and guidelines
*   [x] **Step 3: Update `project_rules.md`**
    *   Remove segments migrated to other modular rules, leaving only core stack metadata
*   [x] **Step 4: Run audit check on rules**
    *   Run `./.agents/scripts/helper.sh list-rules` to verify compliance of all rule files
*   [x] **Step 5: Run workspace validation**
    *   Validate workspace status using `./.agents/scripts/helper.sh validate`
*   [x] **Step 6: Update task state, commit, and unlock**
    *   Set checklist to `[x]` and commit the modular rules
