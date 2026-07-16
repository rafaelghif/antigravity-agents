---
name: code-review
description: Guidelines and checklists for performing high-quality, zero-regression code reviews.
---

# Code Review Skill

This playbook outlines the standards for auditing pull requests, commits, and changes in this repository.

## Review Checklist
1. **Safety & Security**: Verify that no credentials, access tokens, or secrets are committed (see [security-audit playbook](file://.agents/skills/security-audit/SKILL.md)).
2. **Linting & Formatting**: Ensure all codebase styles adhere to project rules.
3. **Layer Decoupling**: Check that business logic is completely isolated from system utilities/scripts (see [coding-standards playbook](file://.agents/skills/coding-standards/SKILL.md)).
4. **Test Coverage**: Validate that all new functions or scripts have corresponding unit tests (see [testing playbook](file://.agents/skills/testing/SKILL.md)).
