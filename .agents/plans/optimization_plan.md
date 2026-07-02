# AAC V2 10/10 Optimization Plan

This document outlines the engineering changes required to optimize the Antigravity Agent Core (AAC) V2 workspace layout and CLI commands to a perfect 10/10 across all core metrics: Strictness, Quality, Performance, and Token Efficiency.

---

## 1. Metric: Strictness (Lock Checks on Unstaged Changes)
*   **Current Score:** 9.5/10 (Locks are only checked for staged files during validation).
*   **Goal:** 10.0/10 (Verify locks on all unstaged changes in the working tree).
*   **Action Plan:**
    1. Update the lock compliance audit in [validate.py](file://./.agents/scripts/validate.py) to check both staged and unstaged files against active locks in `locks.json`.
    2. Prevent validation passing if any file in the working tree is modified but its module is not locked by the current branch.

---

## 2. Metric: Quality (Auto-Formatting Integration)
*   **Current Score:** 9.2/10 (Linting checks syntax correctness but does not enforce style auto-formatting).
*   **Goal:** 10.0/10 (Automatically format modified files using local project tools).
*   **Action Plan:**
    1. Enhance `auto_lint_file()` in [validate.py](file://./.agents/scripts/validate.py) to run formatting tools if they are available in the path:
        *   **Python:** Run `black` or `yapf` on modified `.py` files.
        *   **JS/TS:** Run `prettier --write` on modified frontend files.
        *   **PHP:** Run `php-cs-fixer` if available.
    2. Add a fallback warning if formatting fails or is unconfigured.

---

## 3. Metric: Performance (Remote Sync Throttling & Caching)
*   **Current Score:** 9.8/10 (urllib remote API requests block for up to 3.0s on pre-commit validation if offline/slow).
*   **Goal:** 10.0/10 (Make local validation runs instantaneous by caching remote sync state).
*   **Action Plan:**
    1. Create a lightweight cache file at `.agents/sync_cache.json` containing the timestamp of the last successful remote GitHub sync.
    2. In `git_api.py` and `validate.py`, if the elapsed time since the last sync is less than 5 minutes (300 seconds), bypass the remote URL request and immediately use local issue files.
    3. Add a `--force` flag to `./helper.sh validate` or `sync` to bypass the cache when needed.

---

## 4. Metric: Token Efficiency (Redundancy Prevention)
*   **Current Score:** 9.5/10 (Outdated rules pruned, but agent can still perform redundant search/list calls).
*   **Goal:** 10.0/10 (Minimize agent token overhead by prohibiting repeated tool invocations).
*   **Action Plan:**
    1. Append a strict token-efficiency rule to [.agents/rules.md](file://./.agents/rules.md):
        *   *Rule:* "The agent MUST record found filepaths in its thinking block and is prohibited from calling search tools (`grep_search`, `list_dir`) for the same files more than once per conversation session."
    2. Enforce compact, conversational-free thought patterns in the prompt layout.

---

## 5. Execution Timeline & Verification
1. **Branch setup:** Checkout `feat/issue-103-optimize-ten`.
2. **Module locks:** Acquire locks on `validate` and `git_api`.
3. **Implementation:** Edit `validate.py` and `git_api.py`.
4. **Validation:** Run `./helper.sh validate` to verify the new local caching, formatting checks, and lock compliance enforcements.
