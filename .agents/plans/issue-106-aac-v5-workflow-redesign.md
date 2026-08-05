# Plan: AAC v5 Reliable Antigravity Workflow (Issue #106)

## 1. Decisions & Architectural Trade-offs
- Official Antigravity CLI v1.1.10 docs govern agents, skills, headless mode, planning, permissions, and verification.
- `AGENTS.md` is the compact always-on policy. Detailed behavior belongs in task-specific skills and explicit custom agents.
- `GEMINI.md` is a compatibility bootstrap only; it points to `AGENTS.md` and never duplicates policy.
- Coding quality is enforced through a short Definition of Done and stack-aware verification, not generic polyglot prose.
- GitHub issue/branch/PR/release policy remains delivery governance and does not block ordinary local exploration or planning.
- Context-loading smoke tests report what the CLI can discover; they do not claim model behavior guarantees.

## 2. Granular Micro-Tasks

### Phase 1: Instruction architecture
- [x] Replace the oversized AGENTS.md, TASK_TEMPLATE, soul, rules, schema, and utils duplication with concise contracts.
- [x] Add discoverable planner, implementer, reviewer, and security-reviewer custom agents.
- [x] Replace broad six skills with concise task-specific skills and validate discovery metadata.

### Phase 2: Verification and quality
- [x] Add stack-aware verification and context-loading/token-budget smoke tests.
- [x] Wire CI for word budgets, agent/skill discovery, structural validation, and workflow consistency.

### Phase 3: Documentation and release
- [x] Synchronize README, compatibility, config, changelog, and official Antigravity workflow guidance.
- [x] Run local and CLI verification, then record evidence.

### Phase 4: Delivery
- [ ] Commit with `Fixes #106`, push, create PR, obtain checks, merge with solo-owner policy, publish release, and clean the branch.
