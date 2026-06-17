# Task Workflow: GitLab and Gitea Integration with Git Profile Rotation

This workflow document acts as the single source of truth for the Gitea/GitLab issue tracker integration, token rotation, and cross-platform compatibility details aligned during the `/grill-me` design interview.

---

## 1. Aligned Design Decisions & Execution Plan

### A. Custom URL & API Provider Resolution
- **Rule**: If standard domain-name heuristics (e.g. `gitea` or `gitlab` in the domain name) do not match a custom local/on-premise remote Git URL, resolve the provider type using explicit configuration properties in `.git_profiles`.
- **Configuration Layout**:
  - `gitea_url` property indicates Gitea hosting (e.g., `<profile>.gitea_url=http://localhost:3000`).
  - `gitlab_url` property indicates GitLab hosting (e.g., `<profile>.gitlab_url=https://gitlab.mycompany.local`).
- **Implementation**: Parse the remote URL domain and check `.git_profiles` matching properties for overrides.

### B. Dynamic Git Profile Rotation on API Failures
- **Rule**: If an issue synchronization API call fails due to rate-limiting (HTTP 429) or authentication/access errors (HTTP 401, 403, or connection failure):
  1. Retrieve the list of configured Git profiles from `.git_profiles` (or `~/.git_profiles`).
  2. Rotate the active profile locally (`git config user.name`, `git config user.email`, and optional SSH key configuration) to the next profile in the list.
  3. Load the corresponding token/URL of the new active profile.
  4. Retry the issue synchronization operation.
  5. If the operation succeeds, keep the rotated profile active to ensure subsequent commits/operations on that branch use the correct credentialed user.
  6. Repeat rotation up to the total number of profiles until success, or exhaust all options and fail.

### C. Standardizing Wrapper Scripts & OS Compatibility
- Ensure helper commands and APIs run cleanly in Windows PowerShell and Unix Bash.

---

## 2. Implementation Steps

1. **Modify `cli/commands/issue.py`**:
   - Refactor `sync_remote_issue()` to support an automatic retry loop with Git profile rotation.
   - On sync failure (when standard API returns `None`), read the list of profiles, rotate the local git profile to the next profile using the core rotation logic (similar to `cli/commands/git_profile.py`), and retry.
2. **Add unit tests**:
   - Create or update tests in `tests/test_issue_command.py` to test the issue sync rotation behavior with mock profiles and mock API calls.
3. **Verify Compliance**:
   - Run the workspace validation script to ensure all rules are followed.

---

## 3. Verification & Testing Actions
- Verify the parser handles local port URLs and overrides successfully.
- Verify that simulated API rate-limits/auth errors trigger the automated Git profile rotation and retry loop.
- Validate cross-platform commands run cleanly on Windows PowerShell and Linux Bash.
