# Pre-Implementation Impact Analysis: Auto-Configuration GPG Signing when Switching Profiles

We evaluate options to implement the auto-configuration of GPG signing.

## Option A: Inline GPG config inside switch_profile
Directly execute subprocess git commands inside the existing switch_profile execution flow.
- **Pros**: None.
- **Cons**: High coupling, makes modular unit testing of the configuration changes hard.

## Option B: Modular `configure_git_signing` helper (Recommended)
Add a helper function `configure_git_signing(gpg_key_id)` in `.agents/scripts/cli/commands/profile.py`. This function will run `git config --local user.signingkey <key>` and `git config --local commit.gpgsign true` if a GPG key ID is provided. If `gpg_key_id` is empty, it unsets `user.signingkey` and sets `commit.gpgsign` to `false`.
- **Pros**: Highly modular, clean unit test isolation, and robust error handling.
- **Cons**: None.

### Downstream Impacts
- Modifies `.agents/scripts/cli/commands/profile.py` to add `configure_git_signing` and call it in `switch_profile`.
- Modifies `.agents/tests/test_profile.py` to assert that the git commands are executed correctly when switching.

**Decision**: **Option B** is selected.
