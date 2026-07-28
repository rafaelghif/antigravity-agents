# Agent Task Execution Template (AAC v4.3 Task-Driven Standard)

**Instructions for the Agent:**
Follow these steps sequentially upon receiving a task.

## 1. Pre-flight & Memory Boot Sequence
- [ ] 1. Read `.agents/brain/soul.md` to align persona, humanized tone, and pair-programming empathy.
- [ ] 2. Read `.agents/brain/rules.md` to absorb project invariants and user corrections.
- [ ] 3. Read `.agents/brain/schema.md` (or domain schemas in `.agents/brain/schemas/`) to enforce Zero-Assumption data contracts.
- [ ] 4. **Check Active Tasks & Resume (Direct Filesystem Scan)**:
  - Perform direct scan on `.agents/plans/*.md`.
  - Check for uncompleted micro-tasks (`- [ ]` or `- [~]`). Restore from `.bak` if file is corrupted.
  - If uncompleted tasks exist, **resume execution immediately** from the first uncompleted micro-task without asking redundant questions.

## 2. Engineering Task Planning Phase (MANDATORY BEFORE CODE EDIT)
- [ ] 1. Create a detailed plan file at `.agents/plans/<task-slug>.md`.
- [ ] 2. Record all direct user decisions, context limits, and `/grill-me` discussion logs under `## 1. Decisions & Architectural Trade-offs`.
- [ ] 3. Create dedicated Git Branch matching task slug (`git checkout -b task/<task-slug>`).
- [ ] 4. Include explicit **Single Source of Truth** links (e.g., `schema.md#table_name`).
- [ ] 5. Breakdown implementation into **Granular Micro-Tasks**:
  - Types/DTOs & Contract Layer
  - Data Access & DB Repositories
  - Controllers, Logic & Route Binding
  - Empirical Verification (Build & Test commands)

## 3. Execution & Atomic Checkpoint Protocol
- [ ] 1. Execute **EXACTLY ONE micro-task at a time** (Zero-Batching Directive).
- [ ] 2. If delegating to a subagent, mark status as `- [~] (Assigned: <subagent_id>)`.
- [ ] 3. Claim POSIX directory lock (`mkdir -p .agents/locks/<md5_hash_of_filepath>.lock` and write `owner.json`) before modifying files.
- [ ] 4. After completing each micro-task, run empirical verification (`npm test`, `tsc`, `pytest`).
- [ ] 5. **Immediately update the plan file**: Change `- [ ]` to `- [x]` for the completed micro-task using `replace_file_content` (maintaining `.bak` copy).
- [ ] 6. Repeat until all micro-tasks in `.agents/plans/<task-slug>.md` are marked `- [x]`.

## 4. Post-flight Cleanup & Gate
- [ ] 1. Delete ephemeral `.agents/scratch/*` notes (coordinated with `system-janitor`).
- [ ] 2. Log task completion and token metrics in `.agents/brain/audit.jsonl`.
- [ ] 3. Release POSIX directory locks under `.agents/locks/`.
