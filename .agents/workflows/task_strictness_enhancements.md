# Task Workflow: Enforce Strict Framework Alignment & Isolation

This task implements the strictness enhancements aligned during the `/grill-me` session.

## 1. Architectural Decisions & Specifications
- **Boundary Auto-Heal**:
  - Update `validate.sh` / `validate.py` and `doctor.sh` / `doctor.py` to inspect `.gitignore` and `.antigravityignore`.
  - Ensure `.agents/locks/*` is ignored, but other `.agents` configurations are tracked.
  - Automatically append correct ignore patterns if they are missing.
- **Budget Block**:
  - Update `validate.sh` / `validate.py` and `helper.py` to check token usage budget.
  - If usage exceeds 95% of the threshold, block all CLI runs (locks, commits, skill runs) and throw a blocking validation error.
- **Leak Prevention Guard**:
  - The pre-commit hook must inspect staged files (`git diff --cached --name-only`).
  - Block the commit if transient files (`.lock` files, `active_api_keys*`, `cooldowns.json`) are staged.
  - Verify that the local `user.email` and `user.name` do not leak unconfigured global identities.
- **Quality & Changelog Parser Gate**:
  - Parse `CHANGELOG.md` to ensure it strictly complies with Keep a Changelog standard format.
  - Check staged files for new `TODO` or `FIXME` comments (e.g. lines containing `+.*TODO` or `+.*FIXME`). If found, fail validation and block the commit.

## 2. Checklist & Implementation Status

- [x] **Boundary Auto-Heal Implementation**
  - [x] Implement `.gitignore` and `.antigravityignore` checks in validation logic
  - [x] Add auto-heal capability for incorrect ignores
- [x] **Strict Budget Block**
  - [x] Update helper CLI and validation script to enforce 95% threshold blockade
- [x] **Leak Prevention Hook Guard**
  - [x] Implement pre-commit checks for staged transient files and git user configurations
- [x] **Quality & Changelog Parser Gate**
  - [x] Add Keep a Changelog parser validation check
  - [x] Add staged code check for new `TODO` / `FIXME` comments
- [x] **Verification & Validation**
  - [x] Run validation suite `./.agents/scripts/helper.sh validate`
  - [x] Perform commit via `./.agents/scripts/helper.sh commit`
