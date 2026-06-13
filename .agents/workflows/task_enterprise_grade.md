# Task: Upgrade Workspace to Enterprise & World-Class Grade

This document logs the design decisions and implementation steps to make the Antigravity Agent Core workspace setup enterprise-grade and globally compatible across all operating systems and environments.

---

## 1. Design Decisions

### 1.1 Cross-OS PowerShell Compatibility (`helper.ps1`)
*   Create a native PowerShell wrapper script `.agents/scripts/helper.ps1` that automatically locates `bash.exe` (Git Bash) on Windows and forwards arguments directly to `helper.sh`.
*   Package this template inside `bootstrap.sh` so it is automatically generated during new workspace installations.

### 1.2 Enterprise-Ready GitHub Actions Workflow (`antigravity.yml`)
*   Automatically create a GitHub Actions CI workflow template at `.github/workflows/antigravity.yml` during workspace bootstrapping.
*   The workflow runs `.agents/scripts/validate.sh` to enforce security scans (credential scans, purity validation, memory limit verification, index compliance) automatically on pushes and pull requests.

---

## 2. Implementation Steps

*   [x] **Step 1: Lock module and update memory.md**
    *   Lock `rules` using `./.agents/scripts/helper.sh lock rules`
    *   Set active task checklist in `.agents/memory.md` to `[/]`
*   [x] **Step 2: Create PowerShell wrapper script**
    *   Implement `.agents/scripts/helper.ps1` to forward commands to `helper.sh`
*   [x] **Step 3: Create GitHub Actions workflow template**
    *   Implement `.github/workflows/antigravity.yml` with checking steps
*   [x] **Step 4: Update installer templates in `bootstrap.sh`**
    *   Add directory creation for `.github/workflows`
    *   Add file generation block for `.github/workflows/antigravity.yml` and `.agents/scripts/helper.ps1`
*   [x] **Step 5: Run validation and commit changes**
    *   Verify status using `./.agents/scripts/helper.sh validate`
    *   Update checklist to `[x]` and commit the files
