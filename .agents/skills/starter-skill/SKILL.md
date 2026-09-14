---
name: starter-skill
description: >-
  Provides a standard workflow template for performing tasks and validations
  in this project. Use when introducing new features, scripts, or operational procedures.
---

# Starter Skill Template

This document provides a reference implementation of a Google Antigravity Skill. Skills serve as step-by-step procedural runbooks loaded by the agent on demand (*Progressive Disclosure*).

---

## Operating Procedure

1. **Context & Requirement Analysis**:
   - Inspect related files and existing patterns before making changes.
   - Check whether external dependencies or native alternatives apply.

2. **Execution**:
   - Execute necessary commands or helper scripts.
   - Make precise, targeted file modifications following workspace guidelines.

3. **Verification & Testing**:
   - Run linter, compiler, or test suites to ensure zero regressions:
     ```powershell
     # Example: check git status or run test commands
     git status
     ```

---

## Skill Authoring Best Practices

- **Third-Person Description**: The YAML frontmatter description must be written in third-person and clearly state *what* the skill does and *when* the agent should invoke it.
- **Progressive Disclosure**: Keep `SKILL.md` concise. Place comprehensive manuals or large reference files into a `references/` subdirectory and link to them.
- **Executable Helpers**: Place reusable automation or helper scripts in a `scripts/` subdirectory.
