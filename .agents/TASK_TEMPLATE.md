# Agent Task Execution Template

**Instructions for the Agent:**
When assigned a task using this template, you MUST follow these exact steps sequentially. Do not skip any step. 
Check off each step internally before moving to the next.

## Pre-flight Checklist
- [ ] 1. Read `.agents/brain/rules.md` to absorb past learnings and corrections.
- [ ] 2. Read `.agents/brain/state.json` and verify current state.
- [ ] 3. Update `.agents/brain/state.json.tmp` with the new task name and `mv` to `state.json` (Atomic write).
- [ ] 4. Log the start of this task in `.agents/brain/audit.jsonl`.
- [ ] 5. Create a specific plan in `.agents/plans/<task-name>.md`.
- [ ] 6. Read the required skill files dynamically using the `view_file` tool (e.g., `.agents/skills/architecture-auditor/SKILL.md`).

## Execution (Orchestration Sequence)
- [ ] 1. **architecture-auditor**: Audit impact before coding.
- [ ] 2. **schema-manager**: Check if DB changes are needed.
- [ ] 3. **execution-manager**: Manage tool dependencies.
- [ ] 4. **Implementation**: Branch out (`feature/` or `bugfix/`) and write code.
- [ ] 5. **ui-a11y-reviewer** & **performance-profiler**: Validate code quality.
- [ ] 6. **security-observability-auditor**: Scan for secrets and metrics (Halt if fails).
- [ ] 7. **git-workflow**: Create PR and ask user for `/merge-confirm <ticket-id>`.

## Post-flight Checklist
- [ ] 1. Delete `.agents/scratch/*` artifacts (if successful).
- [ ] 2. Update `state.json` back to `idle`.
- [ ] 3. Log completion in `audit.jsonl`.
