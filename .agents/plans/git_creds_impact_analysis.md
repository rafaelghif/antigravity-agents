# Pre-Implementation Impact Analysis: Git HTTPS Credentials Rotation Integration

## 1. Explore Options

We compare two design options for rotating HTTPS Personal Access Tokens (PATs) when switching between developer profiles in our workspace.

### Option A: Custom Git Credential Helper CLI Command
Configure Git's local `credential.helper` dynamically when switching profiles to route credential resolution through our helper:
```bash
git config --local credential.helper "!python3 .agents/scripts/cli/helper.py profile credential-helper"
```
The helper command parses the Git query from `stdin` (`protocol=https`, `host=github.com`), reads the active profile from `.agents/git_profiles.json`, and outputs `username` and `password` (token) to `stdout` following the official Git Credential Helper protocol.

### Option B: Remote URL Authentication Rewriting
Modify the Git remote URL directly on profile switch to inject the username and token:
```bash
git remote set-url origin https://<email>:<token>@github.com/owner/repo.git
```

---

## 2. Trade-offs Matrix

| Criteria | Option A: Credential Helper (Recommended) | Option B: Remote URL Rewriting |
|---|---|---|
| **Security** | **High**: Tokens are kept securely inside the gitignored `.agents/git_profiles.json`. They are never written to the local `.git/config` or logged in plain text. | **Low**: Plaintext tokens are written to `.git/config` and leaked to terminal output when running `git remote -v`. |
| **Native Git Parity** | **High**: Works seamlessly with any native Git command (`git push`, `git pull`, `git clone`) executed in any terminal environment. | **Medium**: Only applies to the modified remotes. Does not scale well with submodules or multiple remotes. |
| **Complexity** | **Medium**: Requires implementing the stdin/stdout Git Credential Helper protocol. | **Low**: Simple string replacement and running a `git` command. |
| **Maintenance** | **Low**: Standardized protocol that does not depend on remote URL string structures. | **High**: Breaks if the remote domain format changes or if multiple remotes/HTTPS submodules are used. |

---

## 3. Downstream Impacts

- **Workspace Level Storage**: Both options store the credentials in the gitignored `.agents/git_profiles.json` which is secure and isolated within the workspace.
- **Git Config Dependency**: Option A uses local config variables (`credential.helper`) which are cleaned up cleanly if the profile is reset/unset.
- **Cross-Platform Compatibility**: Option A works on both Linux/Mac and Windows since `python3` is globally resolved.

---

## 4. Recommendation

We choose **Option A (Custom Git Credential Helper)** because it offers robust native integration with Git while maintaining maximum credential security (never leaking tokens into `.git/config` or terminal outputs).
