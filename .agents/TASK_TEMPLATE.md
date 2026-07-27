# Agent Task Execution Template (AAC v4.2)

**Instructions for the Agent:**
Follow these steps sequentially upon receiving a task.

## 1. Pre-flight & Memory Boot Sequence
- [ ] 1. Read `.agents/brain/soul.md` to align persona, tone, and empathy.
- [ ] 2. Read `.agents/brain/rules.md` to absorb project invariants and corrections.
- [ ] 3. Read `.agents/brain/schema.md` (or domain schemas in `.agents/brain/schemas/`) to enforce Zero-Assumption data contracts.
- [ ] 4. Read `.agents/brain/state.json` to inspect `session_id`, active branch, token metrics, and claimed task locks.
- [ ] 5. **Select Execution Tier**:
  - **Tier 1 (Quick Fix)**: Skip planning overhead; perform direct edit, verification, and commit.
  - **Tier 2 (Feature)**: Create plan in `.agents/plans/<task-name>.md`, branch, and run test verification.
  - **Tier 3 (Architecture/Major)**: Full audit cycle + multi-agent delegation.
- [ ] 6. Atomic write updated state to `.agents/brain/state.json.tmp` and `mv` to `state.json`.


## 2. Execution & Delegation Protocol
- [ ] 1. **Multi-Agent Delegation Check**: If task requires deep research (> 5 files) or independent sub-features, launch subagent (`invoke_subagent`).
- [ ] 2. **Task Lock**: Claim subtasks in `state.json -> claimed_tasks` before writing files.
- [ ] 3. **Verification Step**: Run project test/build commands (`npm test`, `pytest`, `cargo test`) before declaring completed.

## 3. Post-flight Cleanup
- [ ] 1. Delete ephemeral `.agents/scratch/*` notes.
- [ ] 2. Reset `state.json` status to `idle`.
- [ ] 3. Log task completion in `.agents/brain/audit.jsonl`.

