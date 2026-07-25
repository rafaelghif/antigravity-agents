---
name: context-optimizer
description: Token janitor that compresses memory and clears obsolete artifacts to prevent LLM context bloat.
instruction: Use periodically during long sessions or when token limits approach 80%.
requires_core: ">=4.1.4"
---
# Context Optimizer Skill (Token Janitor)

## Objective
To preserve the agent's cognitive capabilities during long-running sessions by proactively summarizing past activities, deleting irrelevant scratch files, and rotating logs to prevent Token Window exhaustion.

## When to Execute
- When the internal token usage metric exceeds 80%.
- At the end of a very complex task before starting a new one.
- When the `.agents/scratch/` directory contains more than 5 files.

## Execution Steps

1. **Artifact Triage**:
   - Scan `.agents/scratch/` and `.agents/incidents/`.
   - Identify files that are no longer actively relevant to the current task.

2. **Summarization (Compression)**:
   - For incident logs or long debugging outputs, read the file and write a 2-3 sentence dense summary containing the core error, the root cause, and the fix.
   - Append this summary to `.agents/brain/rules.md` if it represents a permanent lesson, or to `.agents/brain/audit.jsonl` as a completed track.

3. **Purge**:
   - Delete the raw, bulky log files and temporary scratch artifacts that have been summarized.
   - Clear out outdated state backups (`state.json.bak.*`) keeping only the most recent one.

4. **Report**:
   - Log a "Context Garbage Collection" event in the audit log, noting how many files were purged to maintain token efficiency.
