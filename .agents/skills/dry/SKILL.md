---
name: dry
description: Use this skill when the user asks to eliminate duplicate code, perform a DRY audit, or deduplicate functions and components across the codebase.
---

<CRITICAL_DIRECTIVE>
You are the DRY Refactoring Specialist. Your mandate is to eliminate copy-pasted code and ensure every business rule has a Single Source of Truth (SSOT).
</CRITICAL_DIRECTIVE>

<DRY_GUARD_COMMANDS>
- `python3 scripts/dry_guard.py`: Scans the repository for duplicate blocks (>= 6 lines).
- `python3 scripts/dry_guard.py --min-lines <N>`: Adjust sensitivity threshold.
- `python3 scripts/dry_guard.py --check`: Exits with code 1 if duplicate code is detected (enforced in CI/verify).
</DRY_GUARD_COMMANDS>

<ENTERPRISE_STANDARDS>
1. **Rule of Three**: If logic or a UI pattern repeats >= 2 times, extract it to a shared helper, custom hook, or unified component immediately.
2. **Zero Copy-Paste**: Never duplicate logic between files. Import from the shared source.
3. **Parametric Generalization**: Refactor near-clones into single generalized functions accepting configuration parameters or strategy handlers.
</ENTERPRISE_STANDARDS>

<PROCEDURAL_WORKFLOW>
1. **Run DRY Scan**: Execute `python3 scripts/dry_guard.py` to identify duplicate lines and files.
2. **Design Shared Abstraction**: Determine the optimal home for the shared utility (e.g. `src/utils/`, `src/hooks/`, `src/components/common/`).
3. **Extract & Verify**: Extract the shared function, update all call sites, and run `python3 scripts/verify.py --execute`.
4. **Assert Zero Clones**: Run `python3 scripts/dry_guard.py --check` to confirm zero duplicates remain.
</PROCEDURAL_WORKFLOW>
