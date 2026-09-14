---
name: caveman-stats
description: >
  Show real session token usage, turn count, and estimated caveman savings from the
  Antigravity conversation transcript. Trigger: /caveman-stats.
---

# Caveman Stats (Antigravity Session Receipts)

Reports turn count, prompt/completion activity, and estimated savings for the current Antigravity session.

## Procedure

1. **Locate Session Transcript**:
   - Transcripts are located at `<appDataDir>\brain\<conversation-id>\.system_generated\logs\transcript.jsonl` (or `<workspace>\.gemini\antigravity\transcript.jsonl`).
   - Read or sample the transcript to count turns (`step_index`), user messages, and model responses.

2. **Calculate Economy**:
   - **Active Caveman Mode**: Determine whether `caveman.md` is active (default: `full`).
   - **Turn Count**: Total number of model and user conversational steps.
   - **Estimated Output Savings**: Based on benchmarked medians:
     - `lite`: ~25% output token reduction.
     - `full`: ~55% output token reduction.
     - `ultra`: ~75% output token reduction.
   - **Rule Overhead**: Estimated input cost of injected caveman rules (~900 chars / ~225 tokens per turn).
   - **Net Savings**: Gross output tokens saved minus cumulative rule overhead.

3. **Output Format**:
   Deliver a concise, tabular summary:
   ```text
   Session Turns:    <N>
   Caveman Mode:     full (active)
   Est. Gross Saved: ~55% output tokens
   Rule Overhead:    ~225 tokens/turn
   Net Economy:      Positive (for technical coding turns > 200 tokens)
   ```
