---
id: issue-021
title: "Refactor CLI command dispatching, validation guard, and git-api error handling"
status: open
assignee: agent-antigravity
created_at: 2026-06-27
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Python 3 (standard library only)
- **Architecture**: Insulation-first refactoring of core utility scripts and CLI commands. Keep modules highly self-contained while improving error robustness.
- **Key Modules**:
  - [validate.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/validate.py): Modulate checks, add run summary block, optimize directory walking.
  - [git_api.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/git_api.py): Standardize to `Bearer` auth, robust remote parsing, add token/remote warnings.
  - [helper.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/helper.py): Simplify subcommand loading/dispatching.
  - [issue.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/issue.py): Handle warnings from GitHub API properly.

## 2. Pre-Implementation Impact Analysis
### Option A: Shared Helper Libraries (DRY Focus)
- **Complexity**: Medium. Requires introducing and managing internal dependency links across commands.
- **Insulation**: Low. Changes to shared helper code might break unrelated subcommands.

### Option B: Self-Contained CLI Modules (Insulation Focus - Recommended)
- **Complexity**: Low. Subcommands remain isolated, self-documenting, and robust.
- **Insulation**: High. Maximizes prompt caching and context insulation, complying with AAC principles.

### Recommendation
Option B is selected. We will keep CLI command modules self-contained while refactoring their internal structure to be cleaner, faster, and more robust.

## 3. Implementation Subtasks
- [ ] **validate.py**: Refactor audits into distinct functions and add a visual audit summary table/box.
- [ ] **validate.py**: Exclude `dist`, `build`, `out`, and `.next` from the secret scanner's directory walker.
- [ ] **git_api.py**: Use `Bearer` token header, robust git remote parse regex, and add warning logs for missing token/remote URL.
- [ ] **helper.py**: Simplify command path loading and error handling.
- [ ] **issue.py**: Clean up arguments parsing and print warning messages if git_api returns `None` for GitHub issue creation.
- [ ] **Tests**: Run unit tests and add new assertions if necessary.
- [ ] **Validation**: Verify `validate.py` runs successfully.

## 4. Acceptance Criteria
- [ ] `validate.py` prints a clean colored Summary Table at the end of the execution.
- [ ] Subcommand runner handles missing or invalid commands gracefully.
- [ ] `helper.py issue create` logs a helpful warning to the user if GITHUB_TOKEN or remote configuration is missing.
- [ ] All unit tests pass.
- [ ] Validation guard runs and passes successfully.
