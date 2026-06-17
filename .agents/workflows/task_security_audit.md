# Task Workflow: Security & Codebase Quality Audit Report

## 1. Objective
Perform a security and code safety audit on all handwritten shell scripts in the Antigravity Agent Core workspace (`.sh` files: `helper.sh`, `validate.sh`, `api-rotate-wrapper.sh`, `recon.sh`), identify potential vulnerabilities (unquoted variables, shell injection, bad word splitting), and implement robust fixes.

---

## 2. Audit Findings

### Finding 1: Unsafe Space-Separated Accumulation (Word Splitting)
- **Files**: `.agents/scripts/validate.sh`
- **Details**:
  - In Check 17 and Check 18, modified files are accumulated as a space-separated string: `MOD_FILES="$MOD_FILES $filepath"`.
  - Loops read these files via `for f in $MOD_FILES` and `for f in $files` without quotes.
  - **Risk**: If any modified or untracked file has spaces in its path/name (e.g. `docs/Release Notes.md` or `tests/my test.py`), the shell will split it into separate arguments, causing verification failures or unexpected script behaviors.
  - **Remediation**: Refactor to use Bash arrays (e.g. `MOD_FILES=()`, `MOD_FILES+=("$file")`) and iterate using `"${MOD_FILES[@]}"`.

### Finding 2: Inconsistent exit-on-error (`set -e`) configuration
- **Files**: `.agents/scripts/api-rotate-wrapper.sh`
- **Details**:
  - The script initializes with `set -uo pipefail` (no `-e`).
  - Later, it toggles `set +e` and `set -e` around command executions.
  - **Risk**: If other setup commands fail prior to line 53, the script may continue in an undefined state.
  - **Remediation**: Explicitly document the reason for omitting `-e` at startup, or initialize `set -euo pipefail` and handle wrapped command exit codes via `"$@"` directly in standard conditional statements.

---

## 3. Checklist & Execution Plan

- [ ] Lock the validation/core module before editing
- [ ] Create local issue #13 for the security audit fixes and checkout its feature branch
- [ ] Refactor Check 17 (`files` accumulation) in `validate.sh` to use Bash arrays
- [ ] Refactor Check 18 (`MOD_FILES` accumulation) in `validate.sh` to use Bash arrays
- [ ] Align and verify all other loop expansions of file lists in `validate.sh`
- [ ] Run validation checks to ensure zero regressions
- [ ] Perform commit, merge, and clean using `helper.sh issue merge`
