# Antigravity 64-Skill Deep Audit Checklist

**Generated**: 2026-09-14T07:25:42.543Z  
**Target Platform**: Google Antigravity (AGY) 2.0 / CLI / Gemini 3.8 Flash (High)  
**Total Skills**: 64  
**Total Dimension Checks**: 512  
**Checks Passed**: 512 (100.0%)  
**Overall Status**: PASSED (100% Compliant)

---

## 1. Summary of Audit Dimensions

Every skill must satisfy 8 strict Antigravity operational criteria:
1. **FM-Syntax**: Valid YAML frontmatter delimiter (`---`).
2. **Name-Match**: Frontmatter `name` exactly equals directory name.
3. **Trigger**: Description specifies explicit 3rd-person trigger (`Use when...` or `Trigger:`).
4. **Clean-FM**: Zero foreign keys (no `tools:`, `model:`, `argument-hint:`, `license:` in frontmatter).
5. **No-Claude**: Zero references to `CLAUDE.md`, `.claude/`, or Claude-specific runtimes.
6. **Native-Tools**: Zero references to generic `Skill` tool (uses `view_file` on `SKILL.md`).
7. **PS-Compat**: Zero `&&` command chaining in PowerShell examples (uses `;`).
8. **No-Placeholders**: Zero unresolved `TODO`, `FIXME`, or `<insert...>` markers.

---

## 2. Batched Checklist by Task Group

### Batch 1: Core Navigation & Compressed Modes (1–10)

| # | Skill Name | Path | Trigger Phrasing | Native Tools | Clean FM | PS Safe | Status |
| :- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| 1 | `ask-matt` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/ask-matt/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 2 | `cavecrew` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/cavecrew/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 3 | `caveman` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/caveman/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 4 | `caveman-commit` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/caveman-commit/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 5 | `caveman-compress` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/caveman-compress/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 6 | `caveman-discover` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/caveman-discover/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 7 | `caveman-evidence-review` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/caveman-evidence-review/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 8 | `caveman-explore` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/caveman-explore/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 9 | `caveman-help` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/caveman-help/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 10 | `caveman-learn` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/caveman-learn/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |

### Batch 2: Observability, Review & Diagnostics (11–20)

| # | Skill Name | Path | Trigger Phrasing | Native Tools | Clean FM | PS Safe | Status |
| :- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| 11 | `caveman-manage` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/caveman-manage/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 12 | `caveman-optimize` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/caveman-optimize/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 13 | `caveman-review` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/caveman-review/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 14 | `caveman-setup` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/caveman-setup/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 15 | `caveman-stats` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/caveman-stats/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 16 | `code-review` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/code-review/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 17 | `codebase-design` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/codebase-design/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 18 | `diagnosing-bugs` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/diagnosing-bugs/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 19 | `domain-modeling` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/domain-modeling/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 20 | `git-guardrails` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/git-guardrails/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |

### Batch 3: Planning, Spec & Implementation (21–30)

| # | Skill Name | Path | Trigger Phrasing | Native Tools | Clean FM | PS Safe | Status |
| :- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| 21 | `grill-me` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/grill-me/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 22 | `grill-with-docs` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/grill-with-docs/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 23 | `grilling` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/grilling/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 24 | `handoff` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/handoff/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 25 | `implement` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/implement/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 26 | `implement-spec` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/implement-spec/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 27 | `improve-codebase-architecture` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/improve-codebase-architecture/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 28 | `investigate-first` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/investigate-first/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 29 | `lean-build` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/lean-build/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 30 | `loop-me` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/loop-me/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |

### Batch 4: Minimalism, De-bloat & Prototypes (31–40)

| # | Skill Name | Path | Trigger Phrasing | Native Tools | Clean FM | PS Safe | Status |
| :- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| 31 | `migrate-to-shoehorn` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/migrate-to-shoehorn/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 32 | `migration` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/migration/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 33 | `ponytail` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/ponytail/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 34 | `ponytail-audit` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/ponytail-audit/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 35 | `ponytail-debt` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/ponytail-debt/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 36 | `ponytail-gain` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/ponytail-gain/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 37 | `ponytail-help` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/ponytail-help/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 38 | `ponytail-review` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/ponytail-review/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 39 | `prototype` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/prototype/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 40 | `research` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/research/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |

### Batch 5: Safety, Refactoring & Setup (41–50)

| # | Skill Name | Path | Trigger Phrasing | Native Tools | Clean FM | PS Safe | Status |
| :- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| 41 | `resolving-merge-conflicts` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/resolving-merge-conflicts/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 42 | `retro` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/retro/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 43 | `safe-refactor` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/safe-refactor/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 44 | `scaffold-exercises` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/scaffold-exercises/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 45 | `setup-matt-pocock-skills` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/setup-matt-pocock-skills/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 46 | `setup-pre-commit` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/setup-pre-commit/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 47 | `setup-ts-deep-modules` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/setup-ts-deep-modules/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 48 | `starter-skill` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/starter-skill/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 49 | `subagent-handoff` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/subagent-handoff/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 50 | `surgical-patch` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/surgical-patch/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |

### Batch 6: Testing, Triage & Autonomous Maps (51–60)

| # | Skill Name | Path | Trigger Phrasing | Native Tools | Clean FM | PS Safe | Status |
| :- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| 51 | `tdd` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/tdd/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 52 | `teach` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/teach/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 53 | `to-questionnaire` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/to-questionnaire/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 54 | `to-spec` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/to-spec/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 55 | `to-tickets` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/to-tickets/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 56 | `triage` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/triage/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 57 | `verify-and-stop` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/verify-and-stop/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 58 | `wait-what` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/wait-what/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 59 | `wayfinder` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/wayfinder/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 60 | `wizard` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/wizard/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |

### Batch 7: Technical Writing & Shaping (61–64)

| # | Skill Name | Path | Trigger Phrasing | Native Tools | Clean FM | PS Safe | Status |
| :- | :--- | :--- | :---: | :---: | :---: | :---: | :---: |
| 61 | `writing-beats` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/writing-beats/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 62 | `writing-for-agents` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/writing-for-agents/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 63 | `writing-fragments` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/writing-fragments/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |
| 64 | `writing-shape` | [SKILL.md](file:///D:/Project/antigravity-agents/.agents/skills/writing-shape/SKILL.md) | ✅ | ✅ | ✅ | ✅ | **✅ PASS** |

---

## 3. Detailed Audit Findings Log

> **All 64 skills passed every audit dimension with 0 defects.**

---

## 4. Cross-Session Resumption Guide

If an agent session is interrupted or context limits are approached:
1. Refer to this checklist to locate the active batch.
2. Read the latest session checkpoint at `.scratch/handoff.md` via `view_file`.
3. Resume execution from the next pending item.
