# Task: Revert Rules to Generic Project-Agnostic State

This document logs the design decisions and steps to restore the workspace rules to a generic, project-agnostic configuration, ensuring maximum flexibility.

---

## 1. Design Decisions

*   Delete modular rule files that were hardcoded to a specific TypeScript/Node/TypeORM stack:
    *   `.agents/rules/db-rules.md`
    *   `.agents/rules/mvc-conventions.md`
    *   `.agents/rules/security-rules.md`
*   Restore `.agents/rules/project_rules.md` to its original generic template (Unknown language, default mock lint/build/test commands).
*   Clean up task workflows and reset the active memory checklist.

---

## 2. Implementation Steps

*   [x] **Step 1: Lock module and update memory.md**
    *   Lock `rules` using `./.agents/scripts/helper.sh lock rules`
    *   Set active task checklist in `.agents/memory.md` to `[/]`
*   [x] **Step 2: Delete modular rule files**
    *   Remove `db-rules.md`, `mvc-conventions.md`, and `security-rules.md`
*   [x] **Step 3: Restore `project_rules.md` to generic template**
    *   Update stack to `Unknown`
    *   Restore mock command outputs for linter/build/test
*   [x] **Step 4: Run workspace validation**
    *   Verify status using `./.agents/scripts/helper.sh validate`
*   [x] **Step 5: Commit changes and release locks**
    *   Update checklist to `[x]` and commit the clean-up
