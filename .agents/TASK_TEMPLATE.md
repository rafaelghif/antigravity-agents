---
description: Advanced 2026 Context Engineering Template for Autonomous Subagents
---

<!--
CRITICAL: All dynamic and static tasks in .agents/tasks/ MUST adhere strictly to this template.
-->
# 🧠 Agent Task Definition (AAC v4.44.3)

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
> Output the structured JSON handoff payload upon completion to `handoff.json`:
> ```json
> {
>   "task_id": "TASK-XXX",
>   "worker_role": "staff-backend",
>   "summary": "Completed feature implementation with zero regressions.",
>   "modifications": [
>     {
>       "filepath": "path/to/file.py",
>       "change_type": "UPDATE",
>       "description": "Implemented core business logic."
>     }
>   ],
>   "tests": [
>     {
>       "test_command": "python3 -m unittest discover tests",
>       "status": "PASSED",
>       "output_snippet": "All tests passed."
>     }
>   ],
>   "confidence_score": 0.95,
>   "requires_human": false
> }
> ```
