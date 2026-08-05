---
name: code-quality
description: Use when implementing or reviewing application code and the user needs correctness, maintainability, tests, or a quality gate.
---

## Checklist
- Inspect complete symbols and existing behavior before editing.
- Preserve public contracts unless the task explicitly changes them.
- Keep the smallest coherent change; avoid speculative abstractions.
- Add or update tests for changed behavior, or report the exact gap.
- Run available formatter, linter, type checker, and tests.
- Review the final diff and error paths.

## Output
Report changed files, verification commands/results, test gaps, and residual risks.
