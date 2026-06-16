# Task Workflow: Modernize Onboarding Guide, Doctor, and Validate UX

This task modernizes the user-facing outputs of the onboarding tutorial (`guide`), diagnostic health checkers (`doctor`), and security compliance check (`validate.sh`). It adds TTY-aware ANSI colors and clean card separations.

## 1. Architectural Decisions & Mappings
- **Target Files**:
  - [guide.py](file://../../.agents/scripts/cli/commands/guide.py) — Interactive tutorial formatting.
  - [doctor.py](file://../../.agents/scripts/cli/commands/doctor.py) — Diagnostic health outputs.
  - [validate.sh](file://../../.agents/scripts/validate.sh) — Compliance scanner.
- **Visual Upgrades**:
  - **guide.py**: Add ANSI colors, bold subtitles, and clean command formatting.
  - **doctor.py**: Color check statuses (Green `[PASS]`, Yellow `[WARNING]`, Red `[FAIL]`).
  - **validate.sh**: Add TTY auto-detection to enable color variables (`GREEN`, `RED`, `YELLOW`, `CYAN`, `BOLD`) only when stdout is a terminal (`[ -t 1 ]`). Colorize statuses and headers.

---

## 2. Implementation Checklist

- [x] **Modernize `guide.py`**
  - Implement color helpers and clean bullet lists in [guide.py](file://../../.agents/scripts/cli/commands/guide.py).
- [x] **Modernize `doctor.py`**
  - Format statuses and command suggestions with colors in [doctor.py](file://../../.agents/scripts/cli/commands/doctor.py).
- [x] **Modernize `validate.sh`**
  - Inject TTY checks and replace plain `[PASS]`, `[WARNING]`, `[FAIL]` with color variables in [validate.sh](file://../../.agents/scripts/validate.sh).
- [x] **Verify and Test**
  - Run diagnostics `./.agents/scripts/helper.sh doctor` and verify colors are printed.
  - Run test suite and ensure no regressions occur.
- [x] **Release locks & Commit**
  - Compile changes into `bootstrap.sh`.
  - Commit final modernized outputs.
