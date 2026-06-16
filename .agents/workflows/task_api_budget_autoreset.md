# Task Workflow: API Budget Auto-Reset

This task adds an automatic token usage reset feature to the API key rotation and budget tracking system. Usage resets are configured globally in `token_budget.json` via a `reset_interval` and triggered when the elapsed time exceeds the interval.

## 1. Architectural Decisions & Mappings
- **Configuration Fields** (added to `token_budget.json` root):
  - `"reset_interval"`: `"hourly" | "daily" | "weekly" | "none"` (or integer seconds). Default: `none`/absent.
  - `"last_reset_timestamp"`: epoch timestamp (integer seconds) indicating when the last reset occurred.
- **Trigger Points**:
  - Automatically evaluated whenever `utils.load_budget()` is called.
  - Ensures a single source of truth across all scripts (CLI, validators, wrappers).
- **Security & Logging**:
  - Prints a console message informing the developer when a budget reset is triggered.
  - Updates `last_reset_timestamp` and writes the reset state back to `token_budget.json`.
- **Grill-Me Alignment Outcomes**:
  - **Supported Intervals**: Supports `"hourly"`, `"daily"`, `"weekly"`, `"monthly"`, and custom integer seconds.
  - **Timestamp Initialization**: Initializes missing `last_reset_timestamp` to the current timestamp. Resets occur after one full interval.
  - **Usage Counts Reset**: Resets both global usage and all profiles' usage counts to 0.
  - **Error Handling**: Invalid interval values are treated as `"none"` with a warning logged.

---

## 2. Implementation Checklist

- [x] **Lock target modules**
  - Run `./.agents/scripts/helper.sh lock cli`
- [x] **Enhance `utils.py` with Auto-Reset Logic**
  - Update [utils.py](file://../../.agents/scripts/cli/utils.py) to parse `reset_interval` and `last_reset_timestamp`.
  - Calculate if interval elapsed:
    - `"hourly"`: 3,600s
    - `"daily"`: 86,400s
    - `"weekly"`: 604,800s
  - Reset `current_token_usage` and all profile usages to 0 if elapsed, then write back with updated `last_reset_timestamp`.
- [x] **Ensure `validate.sh` triggers reset check**
  - Update [validate.sh](file://../../.agents/scripts/validate.sh) Check 9 to run a fast Python one-liner `python3 -c "import sys; sys.path.insert(0, '.agents/scripts/cli'); import utils; utils.load_budget()"` before reading with `jq`.
- [x] **Align `api-rotator/scripts/main.py`**
  - Update [main.py](file://../../.agents/skills/api-rotator/scripts/main.py) to import `utils.py` and call `utils.load_budget()` in `check_and_rotate_budget()` instead of opening the file manually.
- [x] **Add Unit Tests**
  - Add test case to [test_rotation.py](file://../../tests/test_rotation.py) that simulates time passage (mocking timestamps) and verifies that the budget resets correctly.
- [x] **Validate & Verify**
  - Run `./.agents/scripts/helper.sh validate` and `python3 tests/test_rotation.py`.
- [x] **Document Changes**
  - Update [CHANGELOG.md](file://../../CHANGELOG.md) under the unreleased or current version section.
- [x] **Release Locks & Commit**
  - Stage changes and commit using `./.agents/scripts/helper.sh commit chore api-profile "add automatic token usage reset feature"`
