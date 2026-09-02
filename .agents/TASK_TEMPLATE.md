---
description: Advanced 2026 Context Engineering Template for Autonomous Subagents
---

<!--
CRITICAL: All dynamic and static tasks in .agents/tasks/ MUST adhere strictly to this template.
-->
# 🧠 Agent Task Definition (AAC v4.39.0)

> **[Role Definition]**
> You are the L9 [Insert Role, e.g., Backend Architect].

> **[Context / State]**
> Treat this as RAM. Only read the following necessary files to gain context:
> - `[file_path_1]`
> - `[file_path_2]`
> *Do not hallucinate APIs. Use `grep_search` if you lack context.*

> **[Constitutional Constraints]**
> - You MUST NEVER use dummy data, `// TODO`, or hardcoded secrets.
> - Zero SHAM tests: Every single code change must be accompanied by non-tautological tests.
> - O(1) HashMaps > O(N^2) loops: Optimize every data lookup.
> - Strict DRY: Reuse existing code instead of inventing duplicates.

> **[Task Deliverable]**
> - Input: [Describe Inputs]
> - Output: [Describe Expected Outputs / Modifications]
> - Target Files:
>   - `[file_to_modify_1]`
>   - `[file_to_modify_2]`

> **[Verification Gate (TDD)]**
> Execute the following verification command before reporting task completion:
> ```bash
> python3 scripts/verify.py --execute
> ```

> **[Handoff Contract]**
> Output the JSON handoff payload upon completion to `.agents/brain/handoff.json`:
> ```json
> {
>   "task_id": "TASK-XXX",
>   "status": "DONE",
>   "modified_files": [],
>   "tests_run": [],
>   "epistemic_evidence": "Verification output logs proving zero regressions."
> }
> ```
