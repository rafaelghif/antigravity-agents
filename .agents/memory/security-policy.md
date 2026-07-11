# 🛡️ SECURITY RUNBOOK & GUIDELINES
### *Security Policies and Workspace Protection Standards in AAC V3*

## 1. Commit Signing (GPG/SSH Keys Verification)
* **Identity Protection**: To prevent developer impersonation in commits, all repository contributions should be signed.
* **Verification Hook**: The local commit-msg and pre-commit hooks verify that the active git contributor profile aligns with the registered GPG key and email inside `.agents/git_profiles.json`.
* **Signing Configuration**: If GPG signing is enabled, the agent verifies the keyring availability of key `4A1D5B` (or profile-specific keys). If keys are absent, signing is temporarily disabled locally to prevent blocking commit pipelines, but a warning is logged.

## 2. Secrets & Credentials Exclusion
* **Strict Blacklist**: No passwords, private API keys, environment files (`.env`), or private configuration mappings may be committed to the repository.
* **Exclusion Control**: The validation guard audits staged files against `.gitignore` and `.antigravityignore`. Private tokens or credentials discovered in files will trigger validation failure and block commits.
* **Secrets Recovery**: If a secret is accidentally staged, run `git restore --staged <file>` immediately. Do not push.

## 3. Git Profile & Contributor Identity Rotation
* **Profiles Registry**: Git identity profiles are declared in `.agents/git_profiles.json` (untracked, bootstrapped from `.agents/git_profiles.example`).
* **Active Profile Switch**: Use `./helper.sh profile switch <profile-name>` to rotate between contributor identity configurations. This automatically updates local git configuration keys (name, email, SSH key paths) securely.

## 4. MCP Servers & External Network Safelist
* **Resource Sandbox**: Terminal and subprocess execution should remain within the workspace boundary.
* **Permitted Connections**: Outbound calls are allowed to:
  * Official Upstream Repository: `https://github.com/rafaelghif/antigravity-agents.git`
  * Local/Configured Gitea instance endpoints
* **Restriction**: Downloading unverified binary payloads or arbitrary remote shell scripts is strictly prohibited.
