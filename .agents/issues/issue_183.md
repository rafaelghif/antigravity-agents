---
id: 183
title: "Fix platform usage parser for table and markdown account breakdowns"
status: closed
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
The token parser fails to parse limits and used quotas for 5-Hour and Weekly limits when the output format is a Markdown table (e.g. `| **5-Hour Rolling** | 474,764 | 95,853 | ... |`) because the parser expects `"Limit"` and `"Used"` keywords. It also fails to parse account and task breakdowns starting with asterisks and bolded identifiers (e.g., `* **rafaelghifari.business@gmail.com**: ...`).

## Pre-Implementation Impact Analysis

### Option A: Enhanced Parsing Logic (Recommended)
- **Implementation**:
  - Add explicit Markdown table column parsing to 5-Hour and Weekly parser sections in `parse_usage_output` using `line.split('|')`.
  - Update account and task breakdown regexes to support bullet lists starting with `*` and markdown bold markers `**`.
- **Pros**: 100% robust, fixes all invalid token calculations, simple.
- **Cons**: None.

---

## Tasks
- [x] Add Markdown table column parsing for 5-Hour and Weekly rolling limits in `parse_usage_output` inside [token.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/cli/commands/token.py).
- [x] Update account and task breakdown regex patterns in `parse_usage_output` to support bullet lists (`*`) and bold markdown `**`.
- [x] Add unit test case in [test_token.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/tests/test_token.py) for the Markdown table and account/task breakdowns.
- [x] Run validation suite to confirm compliance.

## Acceptance Criteria
- [x] Markdown table format correctly syncs 5-Hour and Weekly limits and used counts.
- [x] Account and task breakdowns are parsed successfully from asterisk/bold formats.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/scripts/cli/commands/token.py <!-- id: audit-target-files -->
- Active module locks:
  - [x] .agents/scripts/cli/commands/token <!-- id: audit-module-locks -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
