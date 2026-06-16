---
name: docs-sync
description: Synchronize inline code comments / docstrings with markdown documentation files.
scripts:
  - scripts/main.py
---

# docs-sync Skill

## 1. Input Specification
- Specify required inputs (e.g., target file paths, options).

## 2. Operational Procedures
1. Run the associated script.
2. Verify results.

## 3. Decision Matrix
- If the script returns success (exit code 0), the action is accepted.
- If the script returns error, it fails.

## 4. Error Mitigation Tree
- Retry execution.
- If it fails, report details back to the user.

## 5. Output Verification Gate
- [ ] Executable script passes all internal checks.
