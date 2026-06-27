---
id: issue-041
title: "Retrieve bootstrapper templates from Git and exclude private/unimportant files during installation/injection"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Python 3, Bash Shell
- **Architecture**: Move baseline configuration generation to Git-tracked template files in the repository. Refactor installer and bootstrapper code to dynamically read templates and sanitize copied files.
- **Key Modules**:
  - [.agents/scripts/cli/commands/bootstrap.py](file://./.agents/scripts/cli/commands/bootstrap.py)
  - [install.sh](file://./install.sh)
- **New Templates**:
  - [.agents/templates/gitignore.template](file://./.agents/templates/gitignore.template)
  - [.agents/templates/antigravityignore.template](file://./.agents/templates/antigravityignore.template)
  - [.agents/templates/python_requirements.txt.template](file://./.agents/templates/python_requirements.txt.template)
  - [.agents/templates/node_package.json.template](file://./.agents/templates/node_package.json.template)
  - [.agents/templates/php_composer.json.template](file://./.agents/templates/php_composer.json.template)

## 2. Implementation Subtasks
- [x] Acquire module locks for `bootstrap` <!-- id: subtask-locks -->
- [x] Create Git-tracked template files under `.agents/templates/` <!-- id: subtask-templates -->
- [x] Refactor `bootstrap.py` to read from the Git-tracked template files rather than manually creating configurations <!-- id: subtask-bootstrap-refactor -->
- [x] Filter out `__pycache__`, `git_profiles.json`, `locks.json`, and other transient/private files during copying in `bootstrap.py` <!-- id: subtask-bootstrap-sanitize -->
- [x] Refactor `install.sh` to explicitly filter out private/unimportant files and ignore patterns from copying <!-- id: subtask-installer-sanitize -->
- [x] Add unit test coverage for template loading and file exclusion/filtering <!-- id: subtask-tests -->
- [x] Release locks, run validation, and merge cleanly <!-- id: subtask-finalize -->

## 3. Acceptance Criteria
- [x] Local tests and `./helper.sh validate` pass successfully
- [x] No hardcoded configuration file templates (e.g. `.gitignore`, `package.json`) exist in `bootstrap.py`
- [x] Transient and private files (e.g. `locks.json`, `git_profiles.json`, `__pycache__`) are never copied to target project directories during installation or bootstrapping
