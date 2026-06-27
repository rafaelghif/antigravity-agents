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

## Loop Detection & Mitigation Protocol

To prevent wasting agent tokens and user budgets, the agent must monitor its own action patterns for loop behaviors.

### A. Recognizing an Infinite Loop
A loop condition is present if:
- You run the same test suite or run command multiple times in a row with the exact same output without modifying files in between.
- You repeatedly search for the same pattern or string in the codebase using `grep_search` or `view_file` calls.
- You repeatedly edit the same file chunk back and forth (e.g. reverting a change then applying it again).
- A validation gate fails, and you run the same repair command without checking if the underlying issue has changed.

### B. Mitigation Actions
1. **Halt Execution**: Stop all automated repair loops immediately once a pattern is executed 3 times without a successful outcome.
2. **Analyze Root Cause**: Before making any further tool call, output a concise diagnostic explanation detailing why the loop occurred.
3. **Request Help**: Present the diagnostic log to the user and ask for clarification, guidance, or code modification permissions rather than continuing the loop.
