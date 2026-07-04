# Pre-Implementation Impact Analysis — Issue-201

Evaluating approaches to enforce early reading of active context and schemas to eliminate initial hallucinations.

## 1. Options Comparison

### Option A: Mandate Early Workspace Reads in Working Protocol (Recommended)
- **Description**: Add a strict rule to `AGENTS.md` non-negotiable rules requiring the agent to read `.agents/active_context.md`, `.agents/schema.md`, and the active issue specification at the beginning of the first turn.
- **Complexity**: Low.
- **Safety**: High. Prevents the model from writing code or plans based on outdated/assumed schema definitions.

### Option B: On-Demand / Late Loading of Schema and Context
- **Description**: Let the model fetch these files only when it believes it needs to edit them.
- **Complexity**: None.
- **Safety**: Low. Often leads to hallucinated schemas in the early design planning phase.

---

## 2. Recommendation
We recommend **Option A** to guarantee strict parity and zero initial design hallucinations.
