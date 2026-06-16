# Workflow Plan: API Rotator Skill & Per-Profile Quota Tracking

This document serves as the single source of truth for the design and implementation of the `api-rotator` skill and the extended per-profile token budget tracking.

---

## 1. Architectural Decisions

- **Per-Profile Quota**: Expand `.agents/token_budget.json` to store token logs per profile name (e.g. `personal`, `work`).
- **`log-usage` subcommand**: Modify `helper.sh log-usage` to:
  1. Default to logging usage to the active profile name in `.agents/active_api_profile_name`.
  2. Support a optional parameter `[profile-name]` to override.
- **Python Runner Skill**: Scaffold a new skill `api-rotator` at `.agents/skills/api-rotator/`. The skill will contain:
  - `SKILL.md`: Documentation of the rotation wrapper.
  - `scripts/main.py`: A Python client wrapper that loads keys from `.agents/active_api_keys`, handles hybrid token budget checks before execution, catches rate-limiting exceptions (`google.api_core.exceptions.ResourceExhausted` / `openai.RateLimitError`), rotates the key, and retries.

---

## 2. Implementation Checklist

- [ ] Modify `helper.sh` (and templates in `bootstrap.sh`) to support per-profile tracking in `log-usage`.
- [ ] Modify `validate.sh` (and templates in `bootstrap.sh`) Check 9 to support per-profile budget checks.
- [ ] Scaffold `api-rotator` skill under `.agents/skills/api-rotator/` with `SKILL.md` and `scripts/main.py`.
- [ ] Document the updates in `README.md` and `CHANGELOG.md`.
- [ ] Verify validation checks pass and commit the final changes.
