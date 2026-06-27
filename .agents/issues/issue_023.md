# Issue 023: Implement Developer Profile Compliance and Stale Lock Auto-Release

## 1. Description
We will implement local developer compliance and conflict-resolution features to simplify multi-developer collaboration and account switching:
1. **Commit-Author Email Validation**: Ensure that the active Git email (`git config user.email`) matches the active profile in `.agents/git_profiles.json` during pre-commit checks.
2. **Onboarding Profile Wizard**: Prompt the user to set up their Git developer profile during interactive project bootstrapping.
3. **Auto-Release Stale Locks**: Automatically prune and clear module locks from `locks.json` if the associated git branch no longer exists locally in the repository.

## 2. Scope & Design Choices
- **Author Validation Check**: Add a sub-check in `.agents/scripts/validate.py`'s Audit 2 to check Git email config against the active profile.
- **Onboarding Wizard**: Modify `.agents/scripts/cli/commands/bootstrap.py` to prompt/warn about profile setup.
- **Stale Lock Pruning**: Update `.agents/scripts/cli/commands/lock.py` to prune stale locks during lock operations, and update `.agents/scripts/validate.py` to auto-prune stale locks during the audit.

## 3. Implementation Subtasks
- [x] **validate.py**: Implement active profile Git email matching verification.
- [x] **validate.py**: Implement stale lock auto-pruning.
- [x] **lock.py**: Implement local branch existence verification and stale lock auto-pruning during lock acquisition/release.
- [x] **bootstrap.py**: Implement interactive Git profile wizard setup and warnings during bootstrap.
- [x] **test_compliance.py**: Write comprehensive unit tests for profile validation, onboarding prompt triggers, and lock auto-release.
- [x] **Validation**: Verify that the entire validation guard runs and passes successfully.

## 4. Acceptance Criteria
- [x] Pre-commit validation fails with a clean error message if the active Git config email doesn't match the email of the active profile in `git_profiles.json`.
- [x] Running interactive project bootstrap guides the user to set up their profile if no profiles are configured.
- [x] Locks associated with deleted or merged local branches are automatically removed from `locks.json` during locking operations or validation checks.
- [x] All unit tests pass.
- [x] Validation guard runs and passes successfully.
