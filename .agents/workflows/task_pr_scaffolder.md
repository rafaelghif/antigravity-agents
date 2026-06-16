# Task Workflow: Implement Git PR Review Scaffolder Skill

This task implements the `pr-scaffolder` skill as aligned during the `/grill-me` session.

## 1. Architectural Decisions & Specifications
- **Command Entrypoint**: `python3 .agents/skills/pr-scaffolder/scripts/main.py`
- **Output Destination**: `.agents/workflows/pr_review_<branch_name>.md`
- **Base Branch Detection**: 
  - Read `.agents/memory.md` -> extract `Active Pull Request Target` (e.g. `main`).
  - Fall back to checking local tracking branch or `origin/main` if not found.
- **Verification Logs**:
  - Run the test command extracted from `.agents/rules/project_rules.md` (e.g. `python3 tests/test_rotation.py`).
  - Capture stdout/stderr verbatim.
  - If tests fail, add a warning badge `> [!WARNING]\n> Verification tests failed!` to the review guide but do not exit.
  - If no test command is configured, output a note badge: `> [!NOTE]\n> No active test runner command configured for this workspace.` and bypass test run.
- **Schema Mapping**:
  - Run `git diff <base_branch> -- .agents/schemas/` to extract schema alterations.
  - Render the differences under the "Schema Changes" section.
- **Code References**:
  - Render absolute links: `[File (Local)](file:///<absolute_path>)`
  - Render relative links: `[File (Repo)](<relative_path>)`
- **Symbol Extraction**:
  - Scan git diff lines for language-agnostic signature regexes (e.g. lines starting with `+def `, `+class `, `+func `, `+type `, etc.) to identify modified classes and functions.
- **Layout & Structure**:
  - Use structured Markdown tables for listing changed files and symbols.
  - Use collapsible `<details>` blocks for rendering verification/test logs to avoid layout clutter.

## 2. Checklist & Implementation Status

- [x] **Scaffold Skill & Test Skeleton**
  - [x] Run `./.agents/scripts/helper.sh create-skill pr-scaffolder "Generates GAP-compliant PR review guides"`
  - [x] Verify test skeleton `tests/test_skill_pr_scaffolder.py` is created
- [x] **Core Logic Implementation**
  - [x] Implement git branch/diff parsing in `.agents/skills/pr-scaffolder/scripts/main.py`
  - [x] Implement test runner execution & output capturing
  - [x] Implement schema diff detection
  - [x] Implement Markdown generator formatting local/repo links
- [x] **Verification & Validation**
  - [x] Run the scaffolded test `python3 tests/test_rotation.py`
  - [x] Run skill audit check `./.agents/scripts/helper.sh list-skills`
  - [x] Verify validation check `./.agents/scripts/helper.sh validate` passes
