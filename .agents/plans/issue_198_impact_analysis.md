# Pre-Implementation Impact Analysis — Issue-198

Evaluating approaches to ensure absolute compliance with workspace-level artifact tracking.

## 1. Options Comparison

### Option A: Enforce Workspace-Level Artifact Constraint in Rules (Recommended)
- **Description**: Add a clear, strict rule to `.agents/templates/rules.md.template` and core `.agents/rules.md` instructing the agent to always write all markdown plans, specifications, designs, and impact analyses strictly under the workspace's `.agents/` folder (e.g. `.agents/plans/` and `.agents/issues/`). This explicitly overrides standard system prompt `<artifacts>` path instructions.
- **Complexity**: Low.
- **Safety**: High. Guarantees that no plans or specifications are lost in global agent directories.

### Option B: Rely on Default Artifact Instructions
- **Description**: Let the system prompt determine where artifacts are written (which defaults to `<appDataDir>/brain/<conversation-id>`).
- **Complexity**: None.
- **Safety**: Low. Violates the user's non-negotiable rule about git tracking and leads to global state pollution.

---

## 2. Recommendation
We recommend **Option A** to guarantee strict workspace-level Git tracking for all AI-generated designs, plans, and alignment specs.
