# Issue 027: Implement Two-Way Git Profile Auto-Sync and Strict Validation

## 1. Description
We will implement a two-way synchronization between the local Git configuration and `.agents/git_profiles.json`. If a developer changes their Git email config manually, the validation guard will auto-detect it, verify if it is registered in `git_profiles.json`, and automatically update the active profile state. If the email is unregistered, validation will fail and block commits.

## 2. Scope & Design Choices
- **Auto-sync active status**: If `git config user.email` matches a registered profile that is inactive in `git_profiles.json`, automatically set it as active and save.
- **Strict blocking gate**: If `git config user.email` does not match any registered profiles in `git_profiles.json`, validation fails to prevent commit.

## 3. Implementation Subtasks
- [x] **validate.py**: Implement matching check and auto-sync of active profile status in `git_profiles.json`.
- [x] **validate.py**: Implement strict blocking for unregistered commit author emails.
- [x] **test_profile_sync.py**: Write unit tests covering matching auto-sync and blocking of unregistered profiles.
- [x] **Validation**: Verify that the entire validation guard runs and passes successfully.

## 4. Acceptance Criteria
- [x] Running validation with a manually changed registered Git email auto-switches the active profile in `git_profiles.json` and passes validation.
- [x] Running validation with an unregistered Git email fails validation and prints a clean instruction on registering profiles.
- [x] All unit tests pass.
- [x] Validation guard runs and passes successfully.
