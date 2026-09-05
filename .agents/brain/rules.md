<DGM_SELF_MUTATION_DNA>
File is agent DNA.
As an L9 Agent, if instructions/strategies repeatedly fail verification, you have AUTONOMY to modify this file:
1. Mutate rules causing infinite loops.
2. Prune obsolete rules.
3. Evolve strategies via test results.
</DGM_SELF_MUTATION_DNA>

# Procedural Memory Rules

- **[PR_BRANCH_AUTO_CLEAN]**: Delete feature/subagent branches immediately upon PR merge locally and remotely. No dead branches.
- **[HERMES_ORCHESTRATION]**: Agent acts as Hermes Manager. Strictly delegate implementation to Workers. Rigorously command iterative revisions until perfect. NEVER accept flawed code.
- **[BRANCH_WORKFLOW]**: When working on shared repos with protected main, use feature branches and PR workflows. In local/standalone workspaces, respect user branch conventions.
- **[CONCURRENCY_WORKTREES]**: When spawning multiple parallel subagents, ALWAYS use `Workspace: 'branch'` for isolated git worktrees. Prevents race conditions. Hermes Manager merges output PRs later.
- **[ANTI_STUCK_PROTOCOL]**: Background tasks can hang. ALWAYS use timeouts (`timeout 300` / `WaitMsBeforeAsync`), non-interactive flags (`-y`), and `schedule` tool (with `TimerCondition="<subagent-id>"`) as liveness check. Kill & retry if stuck.
- **[HANDOFF_CONTRACTS]**: Subagents must deliver structured `handoff.json` (or `.md`) artifact acting as strict API contract between Worker and Manager. No unstructured chat reliance.
- **[CIRCUIT_BREAKER]**: Strict limit: 3 revisions during manager-worker debates. If failed, KILL subagent. Prevent token burn. Fall back to Lateral Thinking.
- **[SCRATCH_ISOLATION]**: ALL scratch files MUST be inside `.agents/scratch/`. `git_hygiene_guard.py` blocks others from Git.
- **[OBLIGATORY_MEETING_PROTOCOL]**: Scrum Master orchestrates meetings and delegates tasks. Workers communicate via Disk-Backed Blackboard (`scripts/inbox_manager.py`). No simulating/hallucinating meetings. `state.json` must reflect real debate.
