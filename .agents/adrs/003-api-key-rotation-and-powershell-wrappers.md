# ADR-003: API Key Rotation and PowerShell Wrappers

## Context
When running agent operations in environments subject to rate limits or API credit boundaries (such as Gemini/OpenAI), hard limits can block task completion. In multi-platform environments (both Linux and Windows PowerShell), a consistent mechanism is required to automatically rotate API credentials and track per-profile token budgets.

## Decision
We implemented a hybrid API profile rotation framework consisting of:
1. **Local Key File (`.agents/api_keys`)**: Configured with multiple named profiles (e.g., `personal`, `work`, `backup`).
2. **Bash Wrapper (`api-rotate-wrapper.sh`)**: Intercepts command executions on Unix, catches rate limit status codes (including `429`, `129`, `3`, and Unix modulo `173`), and rotates keys at runtime.
3. **PowerShell Wrapper (`api-rotate-wrapper.ps1`)**: Intercepts command executions on Windows PowerShell, supports equivalent rotation, and allows dot-source auto-loading of keys.
4. **Token Budget Guard**: Tracks per-profile token consumption dynamically inside `.agents/token_budget.json`, checking usage before requests (proactive) and tracking after success.

## Consequences
- **Positive**: Seamless rate-limit bypass across both Unix (Bash) and Windows (PowerShell) development setups.
- **Positive**: Prevention of budget overruns via profile-level tracking.
- **Neutral**: Modulo wrapping logic (exiting with 173 instead of 429 on Linux) must be accounted for in Unix test suites.
- **Negative**: Key configuration requires manual setup of `.agents/api_keys` before wrappers can function.
