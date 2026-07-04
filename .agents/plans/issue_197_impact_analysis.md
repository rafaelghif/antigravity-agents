# Pre-Implementation Impact Analysis — Issue-197

Evaluating approaches to prevent local transient agent files from leaking into target project Git commits.

## 1. Options Comparison

### Option A: Complete Transient Exclusions in Gitignore Template (Recommended)
- **Description**: Add all transient agent states (locks, logs, tokens, active context, sync cache, upgrade state, archives) to `.agents/templates/gitignore.template` so target projects ignore them by default.
- **Complexity**: Low.
- **Maintainability**: High.
- **Safety**: High. Fully prevents leakage of operational metadata to the target project's repositories.

### Option B: Basic Exclusions Only
- **Description**: Only ignore `locks.json` and `git_profiles.json`, relying on developers to maintain local ignores for the rest.
- **Complexity**: None.
- **Safety**: Low. High risk of committing local logs or token tracking files.

---

## 2. Recommendation
We recommend **Option A** to ensure maximum compliance, safety, and compatibility out-of-the-box for target projects.
