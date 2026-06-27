# Pre-Implementation Impact Analysis

## Issue ID: issue-035
## Title: Improve auto-reconnaissance system to generate structured recommendations report

This analysis compares the chosen design options for this task.

---

### Option A: Real-Time Scanning & Markdown Report Generation (Recommended)
This option updates `.agents/scripts/recon.py` to perform deep analysis of the codebase:
1. **Directory Scanning**: Check if standard folders corresponding to the detected stack are present (e.g. `src/`, `tests/` for Python; `app/`, `tests/` for Laravel).
2. **Dependency Analysis**: Read `requirements.txt`, `package.json`, or `composer.json` to verify if test frameworks and linters are present.
3. **Gitignore Auditing**: Check if standard ignores are present (e.g. `venv`, `node_modules`, `vendor`).
4. **Report Generation**: Compile all findings and write a clean, readable report to `.agents/plans/recon_recommendations.md`.

#### Pros:
- Programmatic, actionable advice.
- Completely isolated file that won't pollute core guidelines or metadata.
- Integrates cleanly with existing helper scripts.

#### Cons:
- Slightly more processing overhead, but only runs during onboarding or manual sync.

---

### Option B: Check & Print recommendations to stdout
Only output warnings to the terminal without writing any report file.

#### Pros:
- Simple.

#### Cons:
- Output is transient; developers or agents cannot easily query the recommendations afterward.

---

### Recommendation
**Option A** is the recommended choice because it creates a persistent, version-tracked report file that can be read by agents to auto-heal missing structures.
