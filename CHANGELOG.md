# Changelog

All notable changes to this project will be documented in this file.


## [2.118.0] - 2026-07-02

### 🚀 Features
- add lock, learn, sync operations and adaptive fast polling

### ⚙️ Chores
- Implement lock, learn, sync, and fast-polling in local dashboard (ISSUE-141)


## [2.117.1] - 2026-07-02

### ⚙️ Chores
- Stage archived issue 138 and 139 specs (ISSUE-140)


## [2.117.0] - 2026-07-02

### 🚀 Features
- add Git profiles and SSH public key management tab and API

### ⚙️ Chores
- Implement Git profile and credentials management in local dashboard (ISSUE-139)


## [2.116.1] - 2026-07-02

### ⚙️ Chores
- Stage archived issue 136 and 137 specs (ISSUE-138)


## [2.116.0] - 2026-07-02

### 🚀 Features
- add active tab visibility-aware auto-polling and update button control
- run compliance audit checks asynchronously in a background thread

### ⚙️ Chores
- Enable asynchronous non-blocking validation audits and auto-updating dashboard (ISSUE-137)

### 🧪 Tests
- assert non-blocking background validation audit behavior


## [2.115.1] - 2026-07-02

### ⚙️ Chores
- Stage archived issue 134 and 135 specs (ISSUE-136)


## [2.115.0] - 2026-07-02

### 🚀 Features
- allow bypassing lock compliance check via environment variables

### ⚙️ Chores
- Add lock compliance bypass switch for human developers (ISSUE-135)


## [2.114.0] - 2026-07-02

### 🚀 Features
- ignore transient agent upgrade check state file

### ⚙️ Chores
- Ignore local upgrade state cache file and stage archived issue 132 (ISSUE-134)


## [2.113.0] - 2026-07-02

### 🚀 Features
- implement non-blocking background auto-upgrade check at CLI exit

### 🛠️ Refactors
- pre-initialize mimetypes at import time

### ⚙️ Chores
- Implement automatic upgrade check for CLI commands (ISSUE-133)
- Enhance dashboard security, scalability, and dynamic MIME type resolution for static files (ISSUE-132)

### 🧪 Tests
- cover automatic upgrade check rate limits and branch validation


## [2.112.0] - 2026-07-02

### 🚀 Features
- serve files dynamically with security guards and mime-type discovery

### ⚙️ Chores
- Enhance dashboard security, scalability, and dynamic MIME type resolution for static files (ISSUE-132)

### 🧪 Tests
- cover dynamic file serving, path traversal guard, and 404 responses


## [2.111.0] - 2026-07-02

### 🚀 Features
- track and commit visual dashboard index.html and style.css static assets

### ⚙️ Chores
- Track dashboard static assets and stage archived issues deletion (ISSUE-131)


## [2.110.0] - 2026-07-02

### 🚀 Features
- create app.js for AJAX loading, tab switching, and task toggling interactivity

### ⚙️ Chores
- Modernize local visual dashboard with modular template serving and interactive subtasks checklist auto-update (ISSUE-130)

### 🧪 Tests
- add unit tests for interactive issue task toggling functionality
- clear env variables to isolate branch alignment subtask unit tests


## [2.109.0] - 2026-07-02

### 🚀 Features
- resolve multi-threading bottlenecks, silence stdout logs, and fix tab browser compatibility ReferenceError
- Fix visual status dashboard UI/UX loading bug, threading HTTP server bottleneck, and terminal stdout clutter (ISSUE-129)


## [2.108.0] - 2026-07-02

### 🚀 Features
- update README and custom skill playbooks for visual dashboard, human validation bypass, and automated board synchronization
- Update user documentation and custom skills to cover visual dashboard, validation bypass, and automated board sync (ISSUE-128)


## [2.107.0] - 2026-07-02

### 🚀 Features
- declare HTML_TEMPLATE as raw string to suppress Javascript regex compiler warnings
- implement human validation bypass, local visual status dashboard, and automatic task board synchronization
- Implement adoption features: Human Bypass Mode, Local Visual Dashboard, and GitHub Issue Task Sync (ISSUE-127)


## [2.106.0] - 2026-07-02

### 🚀 Features
- reduce prompt token footprint, prevent duplicate rules, and mandate active context manifest reads
- Optimize prompt token footprint, prevent duplicate self-learning rules, and prune redundant CLI context (ISSUE-126)


## [2.105.0] - 2026-07-02

### 🚀 Features
- enforce descriptive commit subjects in AGENTS.md, rules.md, and validator checks
- Improve commit message rules in AGENTS.md and rules.md to enforce descriptive subjects (ISSUE-125)


## [2.104.0] - 2026-07-02

### 🚀 Features
- append local issue titles and format Refs trailer in release commits
- Improve release commit messages by injecting local issue titles and formatting Refs trailer (ISSUE-124)


## [2.103.0] - 2026-07-02

### 🚀 Features
- implement path-resolved locks, env token lookup, cached branch checks, and GPG/SSH auto-repair switch
- Implement core design improvements: path-resolved module locks, environment token lookup, and interactive GPG/SSH auto-repair switch (ISSUE-123)


## [2.102.0] - 2026-07-02

### 🚀 Features
- cap ThreadPoolExecutor workers in validate.py to prevent CPU thrashing
- Fix security vulnerabilities and performance bottlenecks identified in critical audit (ISSUE-122)

### 🐛 Bug Fixes
- add --no-install flag to npx calls to secure formatting fallbacks
- remove implicit shell=True parameter and use explicit argument array
- add HTTP timeout parameter to all urlopen requests


## [2.101.0] - 2026-07-02

### 🚀 Features
- Fix Git profile fallback to local user account priority (ISSUE-121)

### 🐛 Bug Fixes
- prevent using placeholder profile in validate auto-repair
- prevent applying placeholder profile in commit command

### 🧪 Tests
- update unit tests for profile fallback and auto-repair behaviors


## [2.100.0] - 2026-07-02

### 🚀 Features
- Execute DX/UX enhancements, fallback lookups for archived tasks, and git performance optimizations (ISSUE-120)


## [2.99.0] - 2026-07-02

### 🚀 Features
- Refactor helper doctor key check validation to warnings instead of hard failures (ISSUE-119)


## [2.98.0] - 2026-07-02

### 🚀 Features
- Position Antigravity CLI as primary highlight in README (ISSUE-118)


## [2.97.0] - 2026-07-02

### 🚀 Features
- Ignore active context archive directory in gitignore (ISSUE-117)


## [2.96.0] - 2026-07-02

### 🚀 Features
- Implement enterprise guardrails: GitHub Action template, active token context archiver, and README marketing pitch rewrite (ISSUE-116)


## [2.95.0] - 2026-07-02

### 🚀 Features
- Optimize documentation and CLI completion prints for onboarding configs (ISSUE-115)


## [2.94.0] - 2026-07-02

### 🚀 Features
- Implement core robustness improvements: headless checks, parallel tests, utf-8 fixes, lockfile tracking, and json schema validation (ISSUE-114)


## [2.93.0] - 2026-07-02

### 🚀 Features
- Track and commit full system audit report in plans (ISSUE-113)


## [2.92.0] - 2026-07-02

### 🚀 Features
- Fix validation audit count and working protocol mismatches in AGENTS.md (ISSUE-112)


## [2.91.0] - 2026-07-02

### 🚀 Features
- Elevate public README.md documentation to world-class enterprise standard (ISSUE-111)


## [2.90.0] - 2026-07-02

### 🚀 Features
- Implement enterprise-grade self-healing database performance and release skills (ISSUE-110)


## [2.89.0] - 2026-07-02

### 🚀 Features
- Optimize validation guard performance and decouple remote sync (ISSUE-109)


## [2.88.0] - 2026-07-02

### 🚀 Features
- Fully benchmark agent core and generate report (ISSUE-108)


## [2.87.0] - 2026-07-02

### 🚀 Features
- add proactive private file scanner and git branch type enforcer
- Implement Proactive Private File Scan and Git Branch Type Enforcer (ISSUE-107)


## [2.86.0] - 2026-07-02

### 🚀 Features
- implement automatic non-interactive mode and commit message format validator
- Implement Automatic Non-Interactive Mode Detection and Commit Message Validation (ISSUE-106)


## [2.85.0] - 2026-07-02

### 🚀 Features
- implement strict task splitting and context insulation rules
- Implement Strict Task Splitting and Context Insulation Protocols in Working Guidelines (ISSUE-105)


## [2.84.0] - 2026-07-02

### 🚀 Features
- Align release version history, resolve double-bumping bug, and format CHANGELOG.md (ISSUE-104)

### 📝 Documentation
- add workspace optimization plan to plans directory

### ⚙️ Chores
- Implement 10/10 Workspace Optimizations for Strictness, Quality, Performance, and Token Efficiency (ISSUE-103)
- align release versions and clean up duplicate changelog entries


## [2.83.0] - 2026-07-02

### 🚀 Features
- Align release version history, resolve double-bumping bug, and format CHANGELOG.md (ISSUE-104)
- Align all versions in core files to 2.83.0 to resolve release duplicates

## [2.82.0] - 2026-07-02

### 🚀 Features
- Implement 10/10 Workspace Optimizations for Strictness, Quality, Performance, and Token Efficiency (ISSUE-103)
- Add lock checks for unstaged changes (working tree changes) to Module Lock Compliance validation
- Integrate auto-formatters (black, prettier, php-cs-fixer) into syntax linting validation
- Implement local sync caching (.agents/sync_cache.json) to throttle GitHub remote requests and speed up pre-commit validation

## [2.81.0] - 2026-07-02

### 🚀 Features
- Prune non-actionable features from rules and lessons learned for token efficiency (ISSUE-102)

### ⚙️ Chores
- Prune changelog-like feature items from lessons-learned and rules.md to optimize agent context tokens

## [2.80.0] - 2026-07-02

### 🚀 Features
- Implement Multi-Language Linting, Graceful Sync Fallbacks, and API Rotation Enhancements (ISSUE-101)
- Add multi-language syntax and lint checks (Python, JS/TS, PHP) and custom lint_command integration
- Catch 401/403 HTTP errors and URLErrors in git_api to prevent raw stack traces on unauthorized/offline states
- Add local offline mode fallback for issue synchronization when unauthorized or offline

## [2.79.0] - 2026-07-02

### 🚀 Features
- Ignore active_context.md in Git and Antigravity ignore configurations (ISSUE-100)

### ⚙️ Chores
- Add .agents/active_context.md to .gitignore and .antigravityignore to prevent developer merge conflicts

## [2.78.0] - 2026-07-02

### 🚀 Features
- Implement Robust Self-Learning and Auto-Sync Guard Integration (ISSUE-099)

### 📝 Documentation
- Record lessons learned for Windows compatibility and GPG keyring auditing diagnostics

## [2.77.0] - 2026-07-02

### 🚀 Features
- Fix Windows compatibility, CLI encoding, and test suite execution bugs (ISSUE-098)


### 🐛 Bug Fixes
- resolve Windows compatibility and Unicode console printing bugs


## [2.76.0] - 2026-06-28

### 🚀 Features
- Enhance safety and type-casting of PowerShell helpers (ISSUE-097)

### 🐛 Bug Fixes
- enforce safe powershell parameter parsing and type casting


## [2.75.0] - 2026-06-28

### 🚀 Features
- Fix parameter parsing error in bootstrap.ps1 on Windows (ISSUE-096)

### 🐛 Bug Fixes
- parameter parsing error in bootstrap.ps1 on Windows


## [2.74.0] - 2026-06-28

### 🚀 Features
- Enhance CLI interactive UX and remove Web Dashboard (ISSUE-095)

### 🐛 Bug Fixes
- implement frontend real-time auto-refresh polling loop
- correct task actions buttons and redesign local dashboard to premium dark style
- register ui subcommand in allowed_commands list
- add visual UI, VS Code integration, and conversational playbooks


## [2.73.0] - 2026-06-28

### 🚀 Features
- Implement visual web dashboard, VS Code extension structure, and conversational workflows (ISSUE-094)

### 🐛 Bug Fixes
- implement incremental validation logic for static analysis and unit testing


## [2.72.0] - 2026-06-28

### 🚀 Features
- Implement incremental static analysis and unit testing in validation guard (ISSUE-093)


## [2.71.0] - 2026-06-28

### 🚀 Features
- Align README.md with PowerShell tab completion and CLI updates (ISSUE-092)

### 🐛 Bug Fixes
- implement unified credentials fallback, GPG diagnostics, and PowerShell completion


## [2.70.0] - 2026-06-28

### 🚀 Features
- Implement unified API credentials, GPG diagnostics, PowerShell completion, and lock auto-pruning (ISSUE-091)

### 🐛 Bug Fixes
- exclude git_profiles.json from tracking and silence validation warnings


## [2.69.0] - 2026-06-28

### 🚀 Features
- Implement workspace security hardening and DX improvements (ISSUE-090)

### 🐛 Bug Fixes
- commit windows installer strict-mode compatibility changes


## [2.68.0] - 2026-06-28

### 🚀 Features
- Synchronize and fix Linux and Windows installation and bootstrap scripts (ISSUE-089)


## [2.67.2] - 2026-06-28

### ⚙️ Chores
- commit interactive switch menu and self-healing hook validations


## [2.67.1] - 2026-06-28

### ⚙️ Chores
- commit interactive profile registration wizard


## [2.67.0] - 2026-06-28

### 🚀 Features
- Implement Interactive Profile Registration Wizard for CLI profile add (ISSUE-088)


## [2.66.1] - 2026-06-28

### ⚙️ Chores
- commit Git identity auto repair fix and tests


## [2.66.0] - 2026-06-28

### 🚀 Features
- Implement Git identity and signing auto-repair fallbacks in validation guard (ISSUE-087)


## [2.65.1] - 2026-06-28

### ⚙️ Chores
- commit GPG signing auto config fix and tests


## [2.65.0] - 2026-06-28

### 🚀 Features
- Implement Auto-Configuration GPG Signing when Switching Profiles (ISSUE-086)


## [2.64.1] - 2026-06-28

### ⚙️ Chores
- commit auto task ID injection hook and tests


## [2.64.0] - 2026-06-28

### 🚀 Features
- Implement Auto-Task ID Injection via prepare-commit-msg Git hook (ISSUE-085)


## [2.63.1] - 2026-06-28

### ⚙️ Chores
- commit upgrade URL and paths fix


## [2.63.0] - 2026-06-28

### 🚀 Features
- Fix upgrade command repository URL and update paths (ISSUE-084)


## [2.62.1] - 2026-06-28

### ⚙️ Chores
- commit two-way issue sync tests and plan


## [2.62.0] - 2026-06-28

### 🚀 Features
- Implement Two-Way Offline-to-Online Issue Synchronization (ISSUE-083)


## [2.61.1] - 2026-06-28

### ⚙️ Chores
- commit sync CLI fix and tests


## [2.61.0] - 2026-06-28

### 🚀 Features
- Fix CLI sync command to compile lessons to rules (ISSUE-082)


## [2.60.1] - 2026-06-28

### ⚙️ Chores
- commit cot compliance impact analysis plan


## [2.60.0] - 2026-06-28

### 🚀 Features
- Implement Chain-of-Thought Compliance Gate in AGENTS.md (ISSUE-081)


## [2.59.1] - 2026-06-28

### ⚙️ Chores
- commit auto-lessons extractor code and tests


## [2.59.0] - 2026-06-28

### 🚀 Features
- Implement Auto-Lessons Extractor when closing issues (ISSUE-080)


## [2.58.0] - 2026-06-27

### 🚀 Features
- Implement Context Optimizer and Self-Learning Memory Rule Synthesizer (ISSUE-079)


## [2.57.0] - 2026-06-27

### 🚀 Features
- Implement DX Improvements (Doctor, Upgrade, Global Launcher, Completion, Docs) (ISSUE-078)


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
