# AI Agent Improvement Roadmap
**Project:** Antigravity Agent Core (AAC) V3  

---

This roadmap outlines a phased strategy for hardening, refining, and scaling the Antigravity Agent Core (AAC) V3 framework to world-class enterprise standards.

---

## Phase 1: Critical Fixes
*Objective: Eliminate configuration leakage, key exposure risks, and dashboard HTTP security gaps.*

### Tasks:
1. **Implement `AAC_HOME` Environment Variable Override**:
   - *Description*: Decouple user home directory references (`~/.gemini`, `~/.ssh`) in `token.py`, `profile.py`, and `dashboard.py`. Allow configuring a custom workspace-isolated base path for global config files.
   - *Dependencies*: None.
   - *Effort*: 1 dev-day (Low complexity).
   - *Expected Outcome*: Global agent configurations can be redirected to any directory, enabling true workspace isolation.
   - *Success Criteria*: No validation warnings emitted for global folder leaks when `AAC_HOME` is active.
2. **Harden Git Profile Token Storage**:
   - *Description*: Restrict plain-text Git PAT configurations inside `.agents/git_profiles.json`. Allow retrieving tokens directly from the process environment (`GIT_PAT` or `GITHUB_TOKEN`).
   - *Dependencies*: None.
   - *Effort*: 1 dev-day (Low complexity).
   - *Expected Outcome*: Security posture is improved by keeping credentials out of persistent files.
   - *Success Criteria*: System resolves Git authentication seamlessly when `git_profiles.json` contains no raw secrets.

---

## Phase 2: Architecture
*Objective: Centralize wrapper command execution, reduce code duplication, and enforce parity checks.*

### Tasks:
1. **Unify Shell Wrapper Parsing Logic**:
   - *Description*: Move CLI argument validation out of `install.sh` / `install.ps1` and `bootstrap.sh` / `bootstrap.ps1` and consolidate command parsing within the Python core command layer.
   - *Dependencies*: Phase 1 completed.
   - *Effort*: 3 dev-days (Medium complexity).
   - *Expected Outcome*: Prevents platform-drift and reduces maintenance overhead of shell scripts.
   - *Success Criteria*: All command arguments and options behave identically on Linux and Windows.
2. **Automate Platform Parity Checks**:
   - *Description*: Enforce automated tests checking file parity between PowerShell scripts and Bash scripts.
   - *Dependencies*: None.
   - *Effort*: 2 dev-days (Low complexity).
   - *Expected Outcome*: Catches script modification gaps early during developer pull request reviews.
   - *Success Criteria*: Pull request validations fail if `helper.sh` and `helper.ps1` are modified without matching edits.

---

## Phase 3: Developer Experience (DX)
*Objective: Improve usability, documentation discoverability, and interactive error resolution.*

### Tasks:
1. **Implement Interactive Fixes in Validation Guard**:
   - *Description*: Update `validate.py` to prompt developers to automatically apply fixes (such as profile switches, lock acquisitions, or branch renames) instead of hard-failing.
   - *Dependencies*: Unify Shell logic.
   - *Effort*: 4 dev-days (Medium complexity).
   - *Expected Outcome*: Reduces friction during validation errors.
   - *Success Criteria*: A developer can run validation, see a branch misalignment error, and resolve it instantly with a single keyboard selection.
2. **Enhance Onboarding Visuals in README**:
   - *Description*: Add terminal execution recordings and a command sitemap flow diagram to the root documentation.
   - *Dependencies*: None.
   - *Effort*: 1 dev-day (Low complexity).
   - *Expected Outcome*: Visual demonstration of commands speeds up developer adoption.
   - *Success Criteria*: README contains links to visual command flows and asciinema captures.

---

## Phase 4: Performance
*Objective: Speed up validation times and optimize memory consumption during log analysis.*

### Tasks:
1. **Implement SQLite transcript and log indexing**:
   - *Description*: Replace linear string parses of `transcript.jsonl` and shell logs in `token.py` with an indexed SQLite db structure.
   - *Dependencies*: None.
   - *Effort*: 3 dev-days (Medium complexity).
   - *Expected Outcome*: Large repository validation runs execute under 500ms.
   - *Success Criteria*: Token budget tracking calculates usage instantly even with 10,000 log lines.

---

## Phase 5: Enterprise Hardening
*Objective: Introduce structured logging, central observability, and robust file lock transaction safety.*

### Tasks:
1. **Integrate Structured JSON Logging**:
   - *Description*: Format all validation and execution logs into standard JSON outputs. Provide integrations for exporting logs to monitoring aggregators.
   - *Dependencies*: None.
   - *Effort*: 3 dev-days (Medium complexity).
   - *Expected Outcome*: Standardized logs simplify enterprise auditing.
   - *Success Criteria*: CLI outputs can be piped directly into log ingestion systems (e.g. ELK, Datadog) without parsing.

---

## Phase 6: Future Scalability
*Objective: Support team-wide concurrent execution and monorepo workspaces.*

### Tasks:
1. **Centralize Concurrency Mutex Locks**:
   - *Description*: Shift from local file-based mutex lockers to Git-branch-metadata or centralized API locking, ensuring agents working across different machines do not experience lock collisions.
   - *Dependencies*: Phase 5 completed.
   - *Effort*: 5 dev-days (High complexity).
   - *Expected Outcome*: Enables multi-developer swarms to work safely on shared repositories without edit conflicts.
   - *Success Criteria*: Lock validation checks succeed and block branch edits when multiple agents edit different scopes concurrently.
