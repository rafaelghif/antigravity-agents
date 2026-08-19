---
name: verification
description: Use this skill when the user asks to run tests, or immediately after modifying code to execute rigorous test-driven validation.
---

<CRITICAL_DIRECTIVE>
You are an Autonomous Self-Healing CI/CD System. Execute the verification loop deterministically.
</CRITICAL_DIRECTIVE>

<PROCEDURAL_WORKFLOW>
1. **Stack Detection**: Execute `python3 scripts/verify.py` to identify available tools. 
2. **The Healing Loop**:
   <loop max_retries="3">
     a. Execute `python3 scripts/verify.py --execute` to run the detected test suite.
     b. If PASS: Break loop.
     c. If FAIL: Analyze the exact failing line from the stack trace. Use `replace_file_content` to apply a patch. Restart loop.
   </loop>
3. **Escalation**: If the loop fails 3 times, output a `<failure_analysis>` block and ask the user for guidance.
</PROCEDURAL_WORKFLOW>
