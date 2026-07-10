---
id: issue-236
title: "chore: upgrade lingering V2 references to V3 in memory and dashboard"
status: closed
assignee: rafaelghif
created_at: 2026-07-10
---

# Issue Details

## Problem Statement
chore: upgrade lingering V2 references to V3 in memory and dashboard

## Tasks
- [x] Upgrade dashboard files from V2 to V3 <!-- id: task-upgrade-dashboard -->
- [x] Upgrade active memory registers (architecture, glossary, lessons-learned, soul, tech-debt) from V2 to V3 <!-- id: task-upgrade-memory -->

## Acceptance Criteria
- [x] Dashboard client and index files are updated to V3 <!-- id: criteria-dashboard-v3 -->
- [x] Memory markdown registers refer to V3 instead of V2 <!-- id: criteria-memory-v3 -->

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] .agents/dashboard/app.js <!-- id: audit-target-files -->
  - [x] .agents/dashboard/index.html <!-- id: audit-target-files-2 -->
  - [x] .agents/memory/architecture.md <!-- id: audit-target-files-3 -->
  - [x] .agents/memory/glossary.md <!-- id: audit-target-files-4 -->
  - [x] .agents/memory/lessons-learned.md <!-- id: audit-target-files-5 -->
  - [x] .agents/memory/soul.md <!-- id: audit-target-files-6 -->
  - [x] .agents/memory/tech-debt.md <!-- id: audit-target-files-7 -->
- Active module locks:
  - [x] .agents/dashboard/app <!-- id: lock-dashboard-app -->
  - [x] .agents/dashboard/index <!-- id: lock-dashboard-index -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
