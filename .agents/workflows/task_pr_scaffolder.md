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
- **Schema Mapping**:
  - Run `git diff <base_branch> -- .agents/schemas/` to extract schema alterations.
  - Render the differences under the "Schema Changes" section.
- **Code References**:
  - Render absolute links: `[File (Local)](file:///<absolute_path>)`
  - Render relative links: `[File (Repo)](<relative_path>)`

## 2. Checklist & Implementation Status

- [ ] **Scaffold Skill & Test Skeleton**
  - [ ] Run `./.agents/scripts/helper.sh create-skill pr-scaffolder "Generates GAP-compliant PR review guides"`
  - [ ] Verify test skeleton `tests/test_skill_pr_scaffolder.py` is created
- [ ] **Core Logic Implementation**
  - [ ] Implement git branch/diff parsing in `.agents/skills/pr-scaffolder/scripts/main.py`
  - [ ] Implement test runner execution & output capturing
  - [ ] Implement schema diff detection
  - [ ] Implement Markdown generator formatting local/repo links
- [ ] **Verification & Validation**
  - [ ] Run the scaffolded test `python3 tests/test_rotation.py`
  - [ ] Run skill audit check `./.agents/scripts/helper.sh list-skills`
  - [ ] Verify validation check `./.agents/scripts/helper.sh validate` passes
