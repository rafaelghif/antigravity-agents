---
name: documentation-engineer
description: Update README, API docs, and inline comments
instruction: Use after making features, architecture changes, or schema updates to ensure documentation stays synchronized.
requires_core: ">=4.0.0"
---
# Documentation Engineer Skill

## Objective
Keep all project documentation in sync with the codebase.

## When to Execute
- Before creating a PR for any user-facing feature or API change.
- When completing a major refactoring.

## Execution Steps
1. Update `README.md` with any new features, configuration steps, or behavioral changes.
2. Update API docs (e.g., OpenAPI, Swagger, or JSON Schema) to reflect new endpoints or modified contracts.
3. Add inline documentation (JSDoc, TSDoc, Python docstrings) for new public functions and methods.
4. Update `CHANGELOG.md` following semantic versioning guidelines.
5. Create a draft for release notes if this closes a milestone.
