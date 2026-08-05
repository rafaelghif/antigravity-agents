# Plan: Align AAC with Antigravity CLI Best Practices (Issue #101)

## 1. Decisions & Architectural Trade-offs
- Official Antigravity CLI documentation is the authority for workspace MCP, skill discovery, permissions, sandboxing, and execution workflows.
- Workspace skills use the documented `.agents/skills/<name>.md` layout. Core compatibility is validated by CI rather than undocumented frontmatter.
- The active plan is tracked so a fresh checkout can recover execution state. Ephemeral audit, scratch, incident, and backup data remains local.
- Installers target the published `v4.3.4` release, preserve local MCP/state, create backups, and fail safely.
- GitHub branch protection is configured remotely after the PR is merged; repository files cannot enforce it alone.

## 2. Granular Micro-Tasks

### Phase 1: Antigravity contracts
- [x] Correct MCP `serverUrl`, flatten skills, add settings baseline, and reconcile the tracked active plan.
- [x] Update AGENTS.md, README.md, schema, and skill references to the documented workspace layout.

### Phase 2: Installation and CI safety
- [x] Harden POSIX and PowerShell installers with strict failure handling, cleanup, backups, release pinning, and local-state preservation.
- [x] Add standard-library structural validation and wire CI permissions, manual dispatch, YAML-independent checks, and validation commands.

### Phase 3: Release and governance
- [x] Pin mutable MCP image references, synchronize version/release documentation, and remove production claims unsupported by controls.
- [x] Run structural, installer, secret, and workflow verification; record results.

### Phase 4: Delivery
- [ ] Commit with `Fixes #101`, push, create PR, obtain approval, merge, tag/release `v4.3.4`, configure main branch protection, and clean the branch.
