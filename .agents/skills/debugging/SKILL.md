---
name: debugging
description: Diagnostic playbook for troubleshooting CLI errors, shell script crashes, and test failures.
---

# Debugging Skill Playbook

Use this playbook when encountering test failures or unexpected system behavior.

## Diagnostic Flow
1. **Verify Prerequisites**: Ensure Python 3 and Git are installed and available in the current PATH.
2. **Path Separators**: On Windows, check if path backslashes (`\`) are causing script syntax errors; ensure paths are dynamically constructed or handled.
3. **Budget Status**: Verify that the daily token limits haven't been exceeded in `token_budget.json`.
4. **Mock State**: Verify that external systems (such as Git remote actions or environment keys) are properly mocked in test suites.
