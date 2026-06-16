# Task Workflow: API Rotation Profile Cooldowns

This document defines the execution plan and architectural decisions for implementing rate-limit cool-off times (cooldowns) in the API auto-rotation wrapper.

---

## 1. Architectural Decisions & Specs

### 1.1 Cooldown Persistence
- **Storage File:** `.agents/cooldowns.json`
- **Gitignore Status:** Ignored by Git (to prevent local rate-limit states from causing git noise).
- **Format:** JSON object mapping profile names to epoch timestamps representing the cooldown expiration time.
  ```json
  {
    "personal": 1718532060,
    "work": 1718532120
  }
  ```

### 1.2 Rotation Logic & Cooldown Check
When `helper.sh api-profile rotate` is called:
1. **Trigger Condition:** The cooldown logic is only triggered if the `--rate-limited` flag is passed (e.g., `helper.sh api-profile rotate --rate-limited`). Manual rotation calls without this flag will cycle profiles directly without placing them on cooldown.
2. Put the **previously active** profile on cooldown for $T$ seconds:
   - Expiry time = Current Time + $T$
   - $T$ is determined by the `API_ROTATION_COOLDOWN_SEC` environment variable (default: `60`).
3. Read available profiles from `.agents/api_keys`.
4. Filter out profiles whose cooldown expiration time is in the future.
5. Select the first available profile that is **not** on cooldown.
6. If **all** profiles are on cooldown:
   - Identify the profile with the earliest cooldown expiration time.
   - Calculate the remaining sleep time.
   - Print a warning message and sleep/wait until that cooldown expires.
   - Select that profile and clear its cooldown.

---

## 2. Implementation Steps

### Step 2.1: Update Gitignore
Ensure `.agents/cooldowns.json` is added to the root `.gitignore` file (this is already handled inside the block guards).

### Step 2.2: Implement Cooldown Logic in `helper.sh`
Modify the `cmd_api_profile()` function in `.agents/scripts/helper.sh`:
- Detect if the target is `rotate` and check if `--rate-limited` is passed.
- If rotating with `--rate-limited`, check the current active profile name and mark it as rate-limited by writing the cooldown entry to `.agents/cooldowns.json` using an inline Python helper.
- Filter candidate profiles using the inline Python script to skip profiles in cooldown.
- If all profiles are in cooldown, calculate the sleep time, wait, and then select the earliest expiring profile.

### Step 2.3: Update Wrapper Scripts and Skills
Modify the rotation calls to include the `--rate-limited` flag:
- In `.agents/scripts/api-rotate-wrapper.sh`
- In `.agents/scripts/api-rotate-wrapper.ps1`
- In `.agents/skills/api-rotator/scripts/main.py`

### Step 2.4: Verify via Tests
Add a test case in `tests/test_rotation.py` to verify that:
1. Rotating a profile with `--rate-limited` puts it on cooldown.
2. If all profiles are on cooldown, the wrapper waits for the cooldown to expire before succeeding.

---

## 3. Verification Plan

- Run `./.agents/scripts/helper.sh validate` to verify syntax and formatting.
- Run `python3 tests/test_rotation.py` to verify all tests pass.
