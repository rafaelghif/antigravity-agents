---
id: issue-349
title: "Improve skill scaffolding CLI remote sync offline registry and verification testing"
status: open
assignee: rafaelghif
created_at: 2026-07-16
---

# Issue Details

## Problem Statement
Improve skill scaffolding CLI, support remote Gitea sync alongside GitHub, implement offline skill caching/registry fallback, and add verification testing subcommand to check skill compliance.

## Pre-Implementation Impact Analysis
- **Option A (Recommended)**: Extend existing `git_api.py` (supporting both GitHub and Gitea seamlessly by checking origin URL and profile envs) and `skill.py` (adding subfolders scaffolding, offline caching lookup, and `skill test` subcommand). Highly backward-compatible and lightweight.
- **Option B**: Scaffold completely new wrapper modules and commands. Higher complexity, increases file size and prompt overhead unnecessarily.

## Tasks
- [ ] Task 1: Scaffold directories structure (`scripts/`, `examples/`, `resources/` with README placeholders) and templates (`validate.py`, `setup.sh`) during `helper.sh skill create`. <!-- id: task-1 -->
- [ ] Task 2: Enhance `git_api.py` to support Gitea. Detect origin url, load Gitea host and access token from git profile or environment variables, and map issue/release calls dynamically. <!-- id: task-2 -->
- [ ] Task 3: Implement local skill caching and offline registry fallback in `skill.py` (cache downloaded skills to `~/.gemini/antigravity-cli/cache/skills/` and load from cache or builtin if offline/git clone fails). <!-- id: task-3 -->
- [ ] Task 4: Add `test` subcommand to `helper.sh skill` (validate `SKILL.md` frontmatter, structure, and run validation hooks). <!-- id: task-4 -->
- [ ] Task 5: Run verification and workspace audits using `./helper.sh validate`. <!-- id: task-5 -->

## Acceptance Criteria
- [ ] `./helper.sh skill create new-skill` creates `scripts/`, `examples/`, `resources/`, `validate.py`, and `setup.sh` templates.
- [ ] `git_api.py` handles Gitea endpoints seamlessly when running on Gitea origin or with `gitea_host` settings.
- [ ] `./helper.sh skill install <skill>` falls back to offline cache/builtin directory if git is offline or URL is a simple name.
- [ ] `./helper.sh skill test <skill>` verifies frontmatter, subdirectories, and executes the validation hook.
- [ ] Validation audit passes successfully.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [ ] `.agents/scripts/git_api.py` <!-- id: audit-git-api -->
  - [ ] `.agents/scripts/cli/commands/skill.py` <!-- id: audit-skill-py -->
- Active module locks:
  - [ ] skill <!-- id: lock-skill -->
  - [ ] git_api <!-- id: lock-git_api -->
  - [ ] test_skill <!-- id: lock-test_skill -->
- Non-negotiable rules checked:
  - [ ] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [ ] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [ ] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
