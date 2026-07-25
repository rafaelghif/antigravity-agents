---
name: advanced-debugger
description: Enforces a scientific, methodical approach to debugging across any tech stack.
instruction: Use whenever a bug is encountered, a test fails, or an unexpected error is thrown.
requires_core: ">=4.1.4"
---
# Advanced Debugger Skill

## Objective
To prevent the agent from blindly guessing solutions or wildly changing code when facing a bug. This skill enforces the "Scientific Debugging Method" using verifiable logging and stack trace analysis.

## When to Execute
- Whenever resolving an issue labeled as a "bug".
- Whenever a test fails during execution.
- Whenever a runtime error or unexpected output occurs.

## Execution Steps

1. **Hypothesis Formulation**:
   - STOP. Do not change the application logic yet.
   - Read the error message or stack trace carefully.
   - Formulate 1-3 hypotheses about what could be causing the issue (e.g., "Null pointer at line X because the API returned empty").

2. **Probe Insertion (Language-Agnostic)**:
   - Insert temporary logging or debugging probes into the code to verify the hypothesis.
   - Use the appropriate syntax for the language:
     - *Python*: `print()`, `logging.debug()`
     - *PHP*: `var_dump()`, `error_log()`
     - *JS/TS*: `console.log()`
     - *Java/C#*: `System.out.println()`, `Console.WriteLine()`
     - *Go*: `fmt.Printf()`

3. **Execution & Evidence Gathering**:
   - Run the specific file, test, or trigger the endpoint.
   - Collect the output of the probes.

4. **Analysis & Targeted Fix**:
   - Did the probe output confirm the hypothesis?
     - **Yes**: Implement the targeted fix for the logic.
     - **No**: Remove the old probes, formulate a new hypothesis, and repeat Step 2.

5. **Cleanup**:
   - Once the bug is fixed, MUST remove all temporary debugging probes (`print`, `console.log`, etc.) before committing the code.
