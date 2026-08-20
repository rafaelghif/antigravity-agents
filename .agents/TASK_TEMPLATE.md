---
description: Advanced 2026 Context Engineering Template for Autonomous Subagents
---

# 🧠 Agent Task Definition (AAC v4.4.41)

> **[Role Definition]**
> You are the L9 [Insert Role, e.g., Backend Architect].

> **[Context / State]**
> Treat this as RAM. Only read the following necessary files to gain context:
> - `[file_path_1]`
> - `[file_path_2]`
> *Do not hallucinate APIs. Use `grep_search` if you lack context.*

> **[Constitutional Constraints]**
> - You MUST NEVER use dummy data, `// TODO`, or hardcoded secrets.
> - You MUST preserve all existing functionality outside this scope.
> - [Insert task-specific constraint, e.g., "Must be O(1) time complexity"]

> **[Task Instructions] (ReAct Pattern)**
> 1. **Reason**: Analyze the file structure and explain your approach in a `<thinking>` block.
> 2. **Act**: Execute the changes step-by-step.
> 3. **Observe**: Run verification (`verify.py`).
> 4. **Reflect**: If verification fails, analyze the stack trace and change your approach (Lateral Thinking).

> **[Output Contract]**
> Once complete, output the following structured response:
> - `<status>`: SUCCESS or ESCALATED
> - `<summary>`: What was changed
> - `<rework_count>`: How many verification loops were needed

> **[Verification Loop]**
> *Before* concluding your task, double-check your own code against the Constitutional Constraints. If you violated a constraint, fix it before returning.
