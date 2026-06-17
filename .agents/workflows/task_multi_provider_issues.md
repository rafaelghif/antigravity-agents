# Task Workflow: Gitea & GitLab Issues Sync and Account Rotation

## 1. Scope & Objective
Add support for local/self-hosted Gitea, GitLab, and other Git providers to the local issue synchronization feature. Enable rotation of provider-specific tokens (`github_token`, `gitlab_token`, `gitea_token`) linked to active Git profiles, ensuring cross-platform compatibility across Linux and Windows without external dependencies.

---

## 2. Design & Implementation Plan

### A. Provider and Remote Auto-Detection (`issue.py`)
1. Extract remote URL from `git remote get-url origin`.
2. Parse the domain name, owner, and repository name.
3. Classify the provider:
   - **GitHub**: if remote URL matches `github.com`.
   - **GitLab**: if remote URL matches `gitlab.com` or has `gitlab` in the domain.
   - **Gitea**: if remote URL contains `gitea`, is hosted on a local IP, or matches local port patterns, or if `<profile>.gitea_url` is configured.
4. Support custom instance URL overrides from active profile properties:
   - `<profile>.gitlab_url`
   - `<profile>.gitea_url`

### B. Rotated Token Lookup
1. Read active profile email from `git config user.email`.
2. Locate the corresponding profile section in `.agents/git_profiles` (or `~/.git_profiles`).
3. Load the token corresponding to the detected provider:
   - GitHub: `<profile>.github_token`
   - GitLab: `<profile>.gitlab_token`
   - Gitea: `<profile>.gitea_token`

### C. Unified Sync Engine
Implement `sync_remote_issue(action, title=None, body=None, remote_issue_number=None)` inside [issue.py](file:///D:/Muhammad%20Rafael%20Ghifari/Software%20Engineer/Application/antigravity-agents/.agents/scripts/cli/commands/issue.py):
- **GitHub API v3**:
  - Base URL: `https://api.github.com/repos/{owner}/{repo}/issues`
  - Auth Header: `Authorization: Bearer {token}`
- **GitLab API v4**:
  - Base URL: `https://{domain}/api/v4/projects/{owner}%2F{repo}/issues`
  - Auth Header: `PRIVATE-TOKEN: {token}`
- **Gitea API v1**:
  - Base URL: `http(s)://{domain}/api/v1/repos/{owner}/{repo}/issues`
  - Auth Header: `Authorization: token {token}`

### D. Metadata Schema & Compatibility
- Add `gitlab_id` and `gitea_id` fields to local issue frontmatter to track issues across providers.
- Maintain the legacy `github_id` field as a fallback alias for backward compatibility.
- Ensure all network operations use `urllib.request` for out-of-the-box Windows & Linux compatibility.

---

## 3. Verification & Testing Plan
- Run existing test suites: `python tests/test_rotation.py`
- Create mock tests to verify provider auto-detection and API URL routing.
