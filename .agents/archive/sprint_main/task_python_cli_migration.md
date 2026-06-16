# Task Workflow: Decompose and Migrate Helper CLI from Bash to Modular Python

This document defines the execution plan and architectural decisions for decomposing the massive, monolithic `helper.sh` (over 4400 lines) into a modular, clean Python package under `.agents/scripts/cli/`.

---

## 1. Architectural Decisions & Specs

### 1.1 Directory Structure
We will scaffold the following modular structure under `.agents/scripts/`:
```
.agents/scripts/
├── cli/
│   ├── __init__.py
│   ├── helper.py              # Entrypoint & CLI Command Router
│   ├── utils.py               # Shared utility functions (logging, file parsing, etc.)
│   └── commands/
│       ├── __init__.py
│       ├── lock.py            # lock / unlock logic
│       ├── validate.py        # Workspace validation logic
│       ├── doctor.py          # doctor check logic
│       ├── migrate.py         # migrate logic
│       ├── git_profile.py     # git-profile configuration
│       ├── api_profile.py     # api-profile configuration
│       ├── recon.py           # codebase reconnaissance call
│       ├── log_usage.py       # log-usage count budget tracking
│       ├── archive.py         # archive active checklist logic
│       ├── skills.py          # list-skills / create-skill logic
│       ├── rules.py           # list-rules / create-rule logic
│       └── init.py            # Project initialization and templates
```

### 1.2 Dispatcher Logic (`helper.py`)
- Reads the sub-command from `sys.argv[1]`.
- Imports and executes the corresponding module dynamically from `commands/` (or calls a mapping).
- Implements standard `--help` and usage prints.

### 1.3 Backward Compatibility (Thin Wrappers)
- We will replace the body of `.agents/scripts/helper.sh` with a thin wrapper:
  ```bash
  #!/usr/bin/env bash
  python3 "$(dirname "${BASH_SOURCE[0]}")/cli/helper.py" "$@"
  ```
- We will replace the body of `.agents/scripts/helper.ps1` with a thin wrapper:
  ```powershell
  $scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
  $helperPy = Join-Path $scriptPath "cli/helper.py"
  python3 $helperPy $args
  ```

---

## 2. Implementation & Migration Steps

### Step 2.1: Scaffold Directory Structure
Create `cli/` and `cli/commands/` directories and empty `__init__.py` files.

### Step 2.2: Implement `utils.py`
Migrate global variables and helper functions from `helper.sh` (e.g., finding the workspace root, reading token budgets, printing formatted titles, loading config properties) into a Python helper module `utils.py`.

### Step 2.3: Migrate Lock & Unlock Commands
Implement `commands/lock.py` containing the logic of `cmd_lock()` and `cmd_unlock()`.

### Step 2.4: Migrate Validation & Doctor Commands
Implement `commands/validate.py` and `commands/doctor.py`. These commands will run linting, check credentials, verify token budgets, and inspect git/api configs.

### Step 2.5: Migrate API Profile and Git Profile Commands
Implement `commands/api_profile.py` and `commands/git_profile.py` including the new rate-limit cooldown persistence (`cooldowns.json`) and profile switching/rotation.

### Step 2.6: Migrate Remaining Utility Commands
- `log_usage.py`
- `archive.py`
- `skills.py`
- `rules.py`
- `recon.py`

### Step 2.7: Migrate Init Command and Templates
Implement `commands/init.py` containing the boilerplate templates (e.g., Next.js, Go Gin, FastAPI config templates). Storing these inside a modular `init.py` ensures they do not bloat runtime execution memory or clutter validation/cooldown editing scopes.

### Step 2.8: Replace Wrappers
Overwrite `helper.sh` and `helper.ps1` with the thin dispatch wrappers.

---

## 3. Verification Plan

- Run `./.agents/scripts/helper.sh validate` to verify the python-based validation passes completely.
- Run `python3 tests/test_rotation.py` to verify that wrappers, rotation, and rate-limit cooldowns work correctly with the new Python CLI backend.
