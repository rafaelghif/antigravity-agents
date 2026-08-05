# Plan: Harden AAC Workflow and Antigravity Compatibility (Issue #103)

## Delivery Status
status: COMPLETE
issue: 103
commit: 6878b87
pull_request: 104
merge_commit: 670c2189527cf629edca423f04e93bf35ceee08f
release: v4.3.5
completed_at: 2026-08-05T13:51:49Z

## 1. Decisions & Architectural Trade-offs
- Official Antigravity CLI documentation is the compatibility authority: best practices, MCP, plugins/skills, permissions, sandbox, headless mode, subagents, and settings.
- Compatibility baseline: Antigravity CLI v1.1.10 as shown by the official documentation navigation fetched on 2026-08-05. Revalidate on CLI major/minor changes.
- The active plan is tracked and must contain explicit delivery metadata before it is considered complete. Boot recovery must not resume a plan whose delivery state is COMPLETE.
- Installers use the immutable `v4.3.5` release ref, stage and validate a complete managed payload before copying, preserve user-managed state, and create a backup for every overwritten managed file.
- `.agents/mcp_config.json` is the Antigravity workspace configuration. `opencode.json` remains an optional ignored OpenCode compatibility file and must be documented as a separate surface.
- Security configuration declares applicability explicitly: repository-level scanners run in CI; language/dependency scanners are not applicable until matching manifests exist.

## 2. Granular Micro-Tasks

### Phase 1: State and compatibility contracts
- [x] Add compatibility metadata, explicit settings permission examples, OpenCode boundary documentation, and completed-delivery state for the existing plan.
- [x] Extend validation to structured release/version checks, recovery state, lock/audit contracts, forbidden artifacts, and scanner applicability.

### Phase 2: Safe workflow and installation
- [x] Make installer comments and README references consistent; stage, validate, preserve, back up, and safely apply release payloads on Linux and Windows.
- [x] Add Windows CI parse/execution coverage and improve CI checks for configuration drift.

### Phase 3: Documentation and governance
- [x] Document exact Antigravity explore/plan/execute, `/agents`, headless, permissions, and MCP workflow without claiming unsupported guarantees.
- [x] Record release/version and branch-protection verification requirements.

### Phase 4: Delivery
- [x] Run all structural/security/installer tests, update this plan with evidence, commit with `Fixes #103`, push, create PR, merge, release, and clean the branch.
