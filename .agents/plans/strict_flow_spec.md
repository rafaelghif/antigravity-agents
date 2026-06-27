# Pre-Implementation Impact Analysis

## Issue ID: issue-028
## Title: Enforce strict git branch flow, merge procedures, and profile identity validation

This analysis compares two implementation options to enforce strict git branch flow and agent protocol guidelines for branching, merging, and identity validation.

---

### Option A: Standardized Validation Guard and Agent Protocol Updates (Recommended)
This option enhances the local validation guard (`.agents/scripts/validate.py`) to strictly enforce git branch names, check for illegal commits on base branches (`main`/`master`), and updates `AGENTS.md` and standard playbooks to dictate strict branch checkout and merge flow rules.

#### Key Features:
1. **validate.py Branch Alignment Gate**:
   - Instead of warning on mismatch, fail when branch names do not align with task/issue patterns.
   - Fail validation if the user/agent is on `main`/`master` and has staged/dirty changes.
2. **Identity Verification**:
   - Keep strict email checking.
3. **Protocol Update in `AGENTS.md`**:
   - Revise "Working protocol" to explicitly require `helper.sh issue checkout <id>` before coding.
   - Revise "Working protocol" to explicitly require merging the branch to `main` upon task completion.

#### Pros:
- Centralized validation. Any code change must pass `validate.py` before commit.
- Standard git commands are used, keeping developer cognitive load minimal.
- Simple, DRY, and completely robust.

#### Cons:
- Developer must manually run checkout/merge commands (or use `helper.sh`), but this is the standard flow.

---

### Option B: Auto-Automation via Custom Scripts
This option adds automated shell scripts or python subcommands (e.g. `./helper.sh issue start` and `./helper.sh issue finish`) that automate the git branch creation, tracking transition, and branch merging under the hood.

#### Key Features:
- `./helper.sh issue start <id>`: transitions task to `Doing` and checks out the branch.
- `./helper.sh issue finish <id>`: runs validation, updates changelog, switches to `main`, merges the branch, and deletes the branch.

#### Pros:
- Less typing for the developer/agent.

#### Cons:
- Introduces script complexity and potential merge conflict failures inside python automation wrappers, which are hard to debug for an agent.
- Higher risk of state mismatch if git commands fail silently.
- Violates KISS (Keep It Simple, Stupid) principle.

---

### Comparison Matrix

| Criteria | Option A (Recommended) | Option B |
| :--- | :--- | :--- |
| **Maintainability** | High (uses existing guard) | Medium (new script logic) |
| **Simplicity** | High (standard git + rules) | Medium (custom wrapper) |
| **Robustness** | High (fails on standard git hooks) | Medium (wrappers can mask errors) |
| **DRY Compliance** | High | Low (duplicates git CLI logic) |

---

### Recommendation
**Option A** is the recommended choice. By strengthening `validate.py` and the core protocol (`AGENTS.md` / `tasking` skill), we enforce the strict flow natively at the Git Hook level (`pre-commit`) and prompt context level, making it robust against bypassing, regardless of which developer identity is used.
