# Changelog

All notable changes to this project will be documented in this file.


## [2.56.0] - 2026-06-27

### 🚀 Features
- Add documentation updates and warranty disclaimer to plan and README (ISSUE-077)


## [2.55.0] - 2026-06-27

### 🚀 Features
- Create Developer Experience DX Improvements Plan (ISSUE-076)


## [2.54.0] - 2026-06-27

### 🚀 Features
- Implement Automated SSH Key Generation for Developer Profiles (ISSUE-075)


## [2.53.0] - 2026-06-27

### 🚀 Features
- Implement Git HTTPS Credentials Rotation Integration (ISSUE-074)


## [2.52.0] - 2026-06-27

### 🚀 Features
- Fix changelog titles and parsing logic (ISSUE-073)


## [2.51.0] - 2026-06-27

### 🚀 Features
- Implement AAC V2 Core Enhancements (Points 1-5) (ISSUE-072)


## [2.50.0] - 2026-06-27

### 🚀 Features
- Sync and resolve bugs in Windows scripts (ISSUE-071)


## [2.49.0] - 2026-06-27

### 🚀 Features
- Fix PowerShell hooks directory resolution path mismatch (ISSUE-070)

### 🐛 Bug Fixes
- resolve hooks destination relative to PowerShell active directory context
- fix python syntax error on windows and unit test compatibility


## [2.48.0] - 2026-06-27

### 🚀 Features
- Fix PowerShell hooks directory resolution path mismatch (ISSUE-070)

### 🐛 Bug Fixes
- fix python syntax error on windows and unit test compatibility


## [2.47.0] - 2026-06-27

### 🚀 Features
- Fix Python syntax error in Windows bootstrap script (ISSUE-069)

### 🐛 Bug Fixes
- fix python syntax error on windows and unit test compatibility


## [2.46.0] - 2026-06-27

### 🚀 Features
- Fix Python syntax error in Windows bootstrap script (ISSUE-069)


## [2.45.0] - 2026-06-27

### 🚀 Features
- Commit install.ps1 path alignment changes (ISSUE-068)


## [2.44.0] - 2026-06-27

### 🚀 Features
- Commit install.ps1 path alignment changes (ISSUE-068)


## [2.43.0] - 2026-06-27

### 🚀 Features
- Align and synchronize installation and bootstrap scripts across OSs (ISSUE-067)


## [2.42.0] - 2026-06-27

### 🚀 Features
- Align and synchronize installation and bootstrap scripts across OSs (ISSUE-067)


## [2.41.0] - 2026-06-27

### 🚀 Features
- Track and commit install.ps1 Windows installer file (ISSUE-066)


## [2.40.0] - 2026-06-27

### 🚀 Features
- Track and commit install.ps1 Windows installer file (ISSUE-066)


## [2.39.0] - 2026-06-27

### 🚀 Features
- Fix Windows installation and bootstrap completeness (ISSUE-065)


## [2.38.0] - 2026-06-27

### 🚀 Features
- Fix Windows installation and bootstrap completeness (ISSUE-065)


## [2.37.0] - 2026-06-27

### 🚀 Features
- Add issue.py to auto-staged files list and commit it (ISSUE-064)


## [2.36.0] - 2026-06-27

### 🚀 Features
- Commit README installation command updates (ISSUE-063)


## [2.35.0] - 2026-06-27

### 🚀 Features
- Fix Windows installation execution policy error (ISSUE-062)

### ⚙️ Chores
- merge bootstrap.py update for projects.json copying


## [2.34.0] - 2026-06-27

### 🚀 Features
- Enforce remote Git source download by default during installation (ISSUE-061)


## [2.33.0] - 2026-06-27

### 🚀 Features
- Improve CLI helper UI, add help commands, and projects.json sample (ISSUE-060)


## [2.32.0] - 2026-06-27

### 🚀 Features
- Copy blueprints directory during install and bootstrap (ISSUE-059)

### 🛠️ Refactors
- auto-update version in bootstrap.ps1 on version bump


## [2.31.0] - 2026-06-27

### 🚀 Features
- Synchronize bootstrap.ps1 versions and verify local file installer options (ISSUE-058)


## [2.30.3] - 2026-06-27

### 🐛 Bug Fixes
- Fix install.sh piping compatibility for unbound BASH_SOURCE variable (ISSUE-057)


## [2.30.2] - 2026-06-27

### 🐛 Bug Fixes
- Fix git_profiles.example comment to be valid JSON (ISSUE-056)


## [2.30.1] - 2026-06-27

### 🐛 Bug Fixes
- Synchronize README.md with CLI commands, monorepo projects, and skills (ISSUE-055)

### 🛠️ Refactors
- upgrade boundary resolution and SemVer prioritization


## [2.30.0] - 2026-06-27

### 🚀 Features
- Refactor changelog generator to improve SemVer safety, boundary resolution, and issue classification (ISSUE-054)

### 📝 Documentation
- add projects.json and contract-synchronization skill for monorepos


## [2.29.0] - 2026-06-27

### 🚀 Features
- Implement monorepo multi-project support and API contract synchronization (ISSUE-053)

### 📝 Documentation
- implement self-learning CLI command and stack-agnostic project auto-detection


## [2.28.0] - 2026-06-27

### 🚀 Features
- Implement self-learning mechanism and plug-and-play stack adaptation (ISSUE-052)

### 📝 Documentation
- remove e2e testing, add token efficiency guidelines, and fix SemVer branch bump mapping


## [2.27.0] - 2026-06-27

### 🚀 Features
- Optimize token efficiency, remove E2E testing, and fix SemVer branch bump (ISSUE-051)

### 📝 Documentation
- add and refactor testing, ci-cd, coding, and security playbooks


## [2.26.0] - 2026-06-27

### 🚀 Features
- Establish Testing and CI-CD playbooks and Refactor existing skills (ISSUE-050)


## [2.25.0] - 2026-06-27

### 🚀 Features
- Fix changelog version bump calculation and branch-based issue injection (ISSUE-049)


## [2.24.0] - 2026-06-27

### 🚀 Features
- Enforce strict security, exploit prevention, and code safety validation rules in `AGENTS.md` and `security-audit/SKILL.md`.


## [2.23.0] - 2026-06-27

### 🚀 Features
- Implement installer prerequisite audits for Git, Python 3, and network connectivity in `install.sh`.


## [2.22.0] - 2026-06-27

### 🚀 Features
- Enforce prompt-level loop guard in `AGENTS.md` and `debugging/SKILL.md` to prevent agent infinite loops.


## [2.21.0] - 2026-06-27

### 🚀 Features
- Implement enterprise-grade Observability & Logging skill playbook and register it in `AGENTS.md` and `README.md`.


## [2.20.0] - 2026-06-27

### 🚀 Features
- Rename custom skills to professional, non-exaggerated enterprise-grade names (`world-class-programmer` -> `coding-standards`, `tasking` -> `task-management`, `adr-writer` -> `adr`, `review` -> `code-review`).
- Update all skill references and descriptions in `AGENTS.md` and `README.md`.


## [2.19.0] - 2026-06-27

### 🚀 Features
- Exclude active project memory, tasks, issues, plans, and internal test suites during installation/injection to guarantee target project isolation.


## [2.18.0] - 2026-06-27

### 🚀 Features
- Retrieve bootstrapper templates dynamically from Git and ignore local git profiles or configurations during installation.
- Whitelist `.template` files from validation lock checks.


## [2.17.0] - 2026-06-27

### 🚀 Features
- Remediate technical debt in issue CLI, validation guard, and bootstrap scripts.
- Support bypass of subtask checks inside validation guard.


## [2.15.0] - 2026-06-27

### 🚀 Features
- Enforce strict git branch flow and base branch edit prohibition.
- Implement two-way profile status auto-sync and strict email blocking.
- Implement two-way remote issue sync with local fallback in validator.
- Implement safe automated installer upgrade with timestamped backup.
- Copy memory templates to target directory in bootstrap.ps1 for Windows systems.
- Isolate target project memory by initializing from clean templates.
- Remove inline templates from bootstrap.ps1 for windows parity.
- Implement developer profile validations and auto-release stale locks.
- Implement auto-changelog and semantic versioning generator CLI.
- Enforce strict Pre-Implementation Impact Analysis and DRY file templates.
- Remove inline templates and enable remote download from github repo.
- Copy standard agent files and skills to target project.
- Modularize validation guard, improve CLI dispatcher and git API error warnings.
- Enforce strict check against ignored files in .gitignore and .antigravityignore.
- Enforce strict workspace-level specifications and artifacts rule.
- Integrate full V2 AGENTS.md template and version sync.
- Implement git profile manager CLI subcommand.
- Establish ADR 0002 for strict validation gate architecture.
- Enforce Git profiles setup rule in agents.md.
- Implement remote GitHub Issue integration and conventional commit msg hook.
- Implement strict Git staged files and private files validation gate.
- Implement V2 CLI project bootstrap subcommand and empty workspace rules.


## [2.14.0] - 2026-06-27

### 🚀 Features
- Implement isolated installer for external project bootstrapping.


## [2.13.0] - 2026-06-27

### 🚀 Features
- Implement V2 CLI mock unit testing suite.


## [2.12.0] - 2026-06-27

### 🚀 Features
- Establish Pre-Implementation Impact Analysis Protocol in working rules and playbooks.


## [2.11.0] - 2026-06-27

### 🚀 Features
- Implement V2 expanded compliance validation suite.


## [2.10.0] - 2026-06-27

### 🚀 Features
- Implement V2 modular Python CLI and wrappers.


## [2.9.0] - 2026-06-27

### 🚀 Features
- Add unresolved subtasks validation guard and tasking design capture skill playbook.


## [2.8.0] - 2026-06-27

### 🚀 Features
- Implement dynamic workspace synchronization script and compile-time validation check.


## [2.7.0] - 2026-06-27

### 🚀 Features
- Enforce strict workspace-level configuration and remove global user config dependencies.


## [2.6.0] - 2026-06-27

### 🚀 Features
- Implement strict Git branch and local Issue validation gates to eliminate agent inconsistency.


## [2.5.1] - 2026-06-27

### 🚀 Features
- Implement offline validation guard, local git hook automation, and windows bootstrap script.


## [2.5.0] - 2026-06-27

### 🚀 Features
- Create universal multi-language bootstrap scripts and documentation templates.


## [2.4.0] - 2026-06-27

### 🚀 Features
- Implement auto-recon script, architectural blueprints, security auditing, and CI/CD workflow.


## [2.3.0] - 2026-06-27

### 🚀 Features
- Add world-class-programmer skill playbook.
- Initialize V2 layout files and update AGENTS.md.


## [2.2.0] - 2026-06-27

### 🚀 Features
- Implement automated issue checkout and git-flow merge lifecycle.
- Implement local issue tracker with helper issue and commit closes integration.
- Modernize onboarding tutorial guide, doctor and validation check outputs with TTY-aware ANSI colors.
- Modernize interactive CLI dashboard with colors and progress indicators.
- Add clean and interactive menu dashboard commands.
- Add guide subcommand and compile python cli files into bootstrap.sh.
- Add push subcommand wrapping validation and profile ssh rotation.
- Add docs-sync specialized skill for docstring synchronization.
- Add automatic token usage reset feature.
- Implement interactive adr wizard skill and validation checks.
- Implement git pr review scaffolder skill.
- Implement strict framework alignment, isolation boundary auto-heals, and budget block gates.
- Design and scaffold git PR review scaffolder skill workflow.
- Implement 4 framework improvements (venv, autocomplete, CI/CD, and skill tests).
- Migrate helper CLI and all subcommands to modular Python.
- Implement API profile rate-limit cooldowns and retry sleep fallback.
