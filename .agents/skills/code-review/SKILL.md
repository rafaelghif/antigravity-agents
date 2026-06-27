---
name: code-review
description: Guidelines and checklists for performing high-quality, zero-regression code reviews.
---

# Code Review Skill

This playbook outlines the standards for auditing pull requests, commits, and changes in this repository.

## Review Checklist
1. **Safety & Security**: No credentials, access tokens, or secrets committed.
2. **Linting & Formatting**: Ensure all Python/Bash styles adhere to project rules.
3. **Layer Decoupling**: Check that business logic is completely isolated from system utilities/scripts.
4. **Test Coverage**: Validate that all new functions or scripts have corresponding unit tests.
