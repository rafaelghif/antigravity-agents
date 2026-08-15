# AAC v4.4.4 Task Template

Use this only for multi-file, architectural, security, or ambiguous work. T1 changes need no plan ceremony.

## Plan

```markdown
# Plan: <title>

## Decisions
- Scope, constraints, source-of-truth files, and user decisions.

## Tasks
- [ ] Explore: inspect relevant symbols, contracts, tests, and stack.
- [ ] Plan: list the smallest implementation and verification steps.
- [ ] Execute: edit only the planned files.
- [ ] Verify: run `python3 scripts/verify.py` or the detected project checks.
- [ ] Review: inspect diff, security/error paths, and residual risks.
```

## Recovery

- Keep one active plan in `.agents/plans/`.
- Archive/delete a plan after delivery is complete; never resume `status: COMPLETE`.
- Back up the plan before changing its checklist.
- Do not claim completion without physical verification output.
