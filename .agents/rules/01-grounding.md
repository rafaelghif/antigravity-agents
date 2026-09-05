---
name: grounding
description: Epistemic codebase grounding and anti-hallucination baseline. Always verify before acting.
trigger: always_on
---

# Epistemic Grounding & Anti-Hallucination Baseline

- **Inspect Before Acting**: ALWAYS run `python3 scripts/grounding.py` and inspect target files via `view_file` before writing or modifying code. Never assume languages, frameworks, package managers, or installed libraries.
- **Repository Reality > Assumptions**: Codebase reality strictly overrides memory and agent preconceptions. If an API, type, or file cannot be verified from local files or official documentation, mark it `UNKNOWN / UNVERIFIED`.
- **Zero Invention**: Never invent non-existent files, functions, CLI flags, packages, or test assertions. Cite verified `file:line` citations for all architectural claims.
