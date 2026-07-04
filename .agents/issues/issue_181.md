---
id: 181
title: "Fix token usage sync and remaining display"
status: open
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
The platform `agy -p "/usage"` output has changed its layout, splitting rolling quota information (Limit, Used, Reset) across multiple lines. The parser in `token.py` is line-based and fails to extract 5-Hour and Weekly limits/used/resets, resulting in out-of-sync quota tracking. Additionally, the CLI does not display remaining tokens (token sisa).

## Pre-Implementation Impact Analysis

### Option A: Multi-line Block Parsing with Keyword Regex (Recommended)
- **Implementation**: Search for "5-Hour" or "Weekly" keywords, extract a 3-line block starting from that line, join the block, and apply robust keyword regex (e.g. `Limit\b[^\d]*([\d,]+)` and `Used\b[^\d]*([\d,]+)`, plus `/` check).
- **Pros**: Clean, decoupling layout order from matching logic. Extremely robust against line swapping/addition. Highly maintainable.
- **Cons**: Slightly larger block extraction regexes.
- **UI/UX**: Clearer and simpler displays.

### Option B: State-Machine Line-by-line Parsing
- **Implementation**: Maintain parsing states (`in_five_hour_section = True`) while iterating.
- **Pros**: Fits the existing line iteration loop.
- **Cons**: Requires complex state flag resets and transition logic. Brittle if line structures deviate.
- **Downstream impact**: High potential for subtle regressions in alternative formats.

### Recommendation
**Option A** is recommended because it is far more robust to formatting variations and avoids complex state machine flags.

---

## Tasks
- [x] Refactor `parse_usage_output` in [token.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/token.py) to parse rolling quotas using multi-line block extraction.
- [x] Add remaining tokens (Limit - Used) display to the `status` command output in [token.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/token.py).
- [x] Update and write unit tests in [test_token.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/tests/test_token.py) to cover the new multi-line platform format.
- [x] Run validation suite to confirm compliance.

## Acceptance Criteria
- [x] `./helper.sh token status` displays correct remaining tokens for Daily, Monthly, 5-Hour, and Weekly quotas.
- [x] `parse_usage_output` successfully parses all 5 formats (table, list, console text, block percentage, and new multi-line platform formats) for 5-Hour and Weekly quotas.
- [x] All unit tests pass successfully.
