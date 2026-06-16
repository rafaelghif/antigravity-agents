# Task Workflow: Python Core & Shell Improvements

This task implements the 4 recommended core system improvements agreed upon with the user.

## 1. Scope of Work & Rationale
- **GitHub Actions CI/CD**: Ensure every PR and change is automated and validated via GitHub Actions before merging, maintaining 100% repository health.
- **Python Virtual Environment (.venv) Isolation**: Auto-detect `.venv` folder in the project root to run helper scripts via the virtual environment's Python binary. Add a bootstrapper option to create it.
- **CLI Shell Auto-Completion**: Enable developers to run `./.agents/scripts/helper.sh autocomplete bash` or `zsh` to load tab-completion.
- **TDD Skeleton Skill Tests**: Extend the `create-skill` command to automatically generate a basic test suite under `tests/test_<skill_name>.py` to encourage Test-Driven Development (TDD).

## 2. Checklist & Implementation Status

- [x] **GitHub Actions Workflow**
  - [x] Create `.github/workflows/verify.yml`
  - [x] Configure it to run workspace validation (`./.agents/scripts/helper.sh validate`) and Python unit tests (`python3 tests/test_rotation.py`)
- [x] **Python Virtual Environment (.venv) Support**
  - [x] Update [helper.sh](file://../../.agents/scripts/helper.sh) to check for `.venv/bin/python` or `.venv/bin/python3`
  - [x] Update [helper.ps1](file://../../.agents/scripts/helper.ps1) to check for `.venv/Scripts/python.exe`
  - [x] Update [bootstrap.sh](file://../../bootstrap.sh) to support `--create-venv` / `-v` flag
- [x] **CLI Shell Auto-Completion**
  - [x] Create [autocomplete.py](file://../../.agents/scripts/cli/commands/autocomplete.py) subcommand
  - [x] Register `autocomplete` command in [helper.py](file://../../.agents/scripts/cli/helper.py)
- [x] **TDD Skeleton Skill Tests**
  - [x] Update [skills.py](file://../../.agents/scripts/cli/commands/skills.py) to generate `tests/test_<skill_name>.py` when creating a skill
  - [x] Verify test discovery works with new structure
