# Task Workflow: Create Comprehensive Layman-Friendly User Guide

## 1. Scope & Objective
Create a detailed, step-by-step user guide (`docs/user_guide.md`) written specifically for developers and non-technical stakeholders. It will clarify the end-to-end integration between the local workspace and the `antigravity-cli` (`agy`) client wrapper.

---

## 2. Design & Implementation Plan

### A. Document Structure (`docs/user_guide.md`)
1. **Introduction**: High-level explanation of how the Antigravity Agent Core workspace coordinates with the `antigravity-cli` tool.
2. **Onboarding & Authentication Flow**:
   - Step-by-step sign-in options (silent local keyring vs. remote SSH OAuth URL loop).
   - How `agy` launches the web browser and secures access tokens.
3. **Session Management**:
   - Logging out via the `/logout` command.
4. **How Prompting and Coding Works**:
   - Writing task descriptions, issue creations, branch lockings, validations, and merging.
5. **How Profile Rotation Works**:
   - **API Key Rotation**: How `api-rotate-wrapper` switches profiles on rate limit (HTTP 429) automatically.
   - **Git Profile Rotation**: How `helper.py commit` and `issue` command switch Git identities (user.name/email/SSH/tokens).

### B. Index Update
- Link the new `user_guide.md` in root `README.md` under the documentation index.

---

## 3. Verification & Testing Plan
- Run the workspace validation script to ensure all markdown links are correct.
