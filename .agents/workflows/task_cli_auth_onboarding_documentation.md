# Task Workflow: CLI Authentication and Onboarding Documentation

## 1. Scope & Objective
Add clear, comprehensive developer documentation detailing the `antigravity-cli` (`agy`) outer-wrapper authentication workflows, keyring credentials storage, remote SSH OAuth fallback flows, prompting guidelines, and session management commands (like `/logout`). This bridges the gap between the inner workspace protocol and the outer CLI client harness.

---

## 2. Design & Implementation Plan

### A. Document Authentication Workflows
Add a new section inside [docs/setup_guide.md](file://./../docs/setup_guide.md) and [README.md](file://./../README.md) detailing the outer CLI sign-in methods:
1. **Local Silent Keyring Sign-In**:
   - Explaining how `agy` accesses native OS secure keyrings (Apple Keychain, Linux Secret Service/dbus, Windows Credential Manager).
   - Silent session authentication details.
2. **Remote SSH OAuth Flow**:
   - Step-by-step description of executing `agy` inside remote SSH environments.
   - Using the printed secure authorization URL on the local web browser.
   - Entering the resulting authorization code into the remote terminal prompt.
3. **Session Management**:
   - Documenting the `/logout` command to purge saved credential profiles and clean local cache directories.
4. **Prompting Guidelines**:
   - Explaining how the interactive agent chatbox behaves after authentication, and how users can prompt the agent to perform coding tasks using the workspace rules.

### B. Execution Steps
- Edit [docs/setup_guide.md](file://./../docs/setup_guide.md) to insert the "Authentication Workflows" section.
- Edit [README.md](file://./../README.md) to register and summarize the CLI authentication command and session logout mechanism.

---

## 3. Verification & Testing Plan
- Run the workspace validation script to ensure all markdown files are compliant and index registrations are valid.
