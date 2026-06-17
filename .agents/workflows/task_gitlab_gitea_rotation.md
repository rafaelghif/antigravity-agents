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
- **Rule**: If an issue synchronization API call fails due to rate-limiting (HTTP 429) or authentication errors (HTTP 401/403):
  1. Retrieve the list of configured Git profiles from `.git_profiles`.
  2. Rotate the active profile locally (`git config user.name`, `git config user.email`, and optional SSH key configuration).
  3. Load the corresponding token/URL of the new active profile.
  4. Retry the issue synchronization operation.

### C. Cross-Platform OS Compatibility
- **Rule**: Standardize all core command logic in unified Python scripts (such as `helper.py`, `utils.py`, and command scripts in `.agents/scripts/cli/commands/`).
- **Shell Wrappers**:
  - Keep `.sh` (Bash/Linux) and `.ps1` (PowerShell/Windows) files as thin wrapper scripts that bootstrap Python execution.
  - Automatically handle environment setups, OS-specific pathing, and console character encodings (e.g. safe emoji-to-ASCII conversion in CP932).

### D. Remote Git Repository Detection
- **Rule**: When resolving git remote URLs, default to detecting the `origin` remote first.
- **Fallback**: Search for alternative remotes (e.g. `upstream` or any configured remote in git config) if `origin` is not set or valid.

---

## 2. Verification & Testing Actions
- Verify the parser handles local port URLs and overrides successfully.
- Verify that simulated API rate-limits/auth errors trigger the automated Git profile rotation and retry loop.
- Validate cross-platform commands run cleanly on Windows PowerShell and Linux Bash.
