---
id: 343
title: "feat: prioritize MCP tools over local for issues pulls mergers and projects"
status: open
assignee: rafaelghif
created_at: 2026-07-16
---

# Issue Details

## Problem Statement
The agent currently prioritizes local tracking for issues, pulls, mergers, and projects. We need to implement a strict rule prioritizing MCP tools (specifically GitHub and Gitea MCP servers) for managing and tracking issues, pull requests, merges, and projects. Bypassing active MCP tools in favor of local files is prohibited unless the MCP server/integration is invalid, unauthorized, or offline. In that case, it should gracefully fall back to local tracking. When MCP is valid, the local states must still be kept synchronized.

## Tasks
- [x] Add the non-negotiable rule prioritizing MCP tools to `.agents/templates/AGENTS.md.template` <!-- id: task-agents-template -->
- [x] Add the non-negotiable rule prioritizing MCP tools to `AGENTS.md` <!-- id: task-agents-core -->
- [x] Document this prioritization in `.agents/templates/rules.md.template` <!-- id: task-rules-template -->
- [x] Document this prioritization in `.agents/rules.md` <!-- id: task-rules-core -->
- [x] Run sync and validate commands to verify parity and cleanliness <!-- id: task-sync-validate -->

## Acceptance Criteria
- [x] Both rules files and their templates are updated and consistent <!-- id: ac-parity -->
- [x] Validation command `./helper.sh validate` passes cleanly <!-- id: ac-validation -->

## Pre-Implementation Impact Analysis
- **Option A**: Implement the priority rule only in `AGENTS.md`.
  - *Pros*: Quick edit.
  - *Cons*: Does not prevent template drift (during bootstrap/upgrade) and leaves `.agents/rules.md` outdated.
- **Option B (Recommended)**: Synchronize the change across `AGENTS.md` and `.agents/rules.md`, along with their templates under `.agents/templates/`.
  - *Pros*: Avoids configuration drift, maintains Linux/Windows/Docker bootstrap consistency, and provides robust multi-layered rule enforcement.
  - *Cons*: Slightly more files to modify, but fully compliant with AAC V3 standard.

## Rule & Schema Compliance Audit
- Target files to edit:
  - [x] `.agents/templates/AGENTS.md.template` <!-- id: target-agents-template -->
  - [x] `AGENTS.md` <!-- id: target-agents-core` -->
  - [x] `.agents/templates/rules.md.template` <!-- id: target-rules-template -->
  - [x] `.agents/rules.md` <!-- id: target-rules-core -->
- Active module locks:
  - [x] `AGENTS.md` locked <!-- id: audit-agents-lock -->
  - [x] `.agents/rules.md` locked <!-- id: audit-rules-lock -->
- Non-negotiable rules checked:
  - [x] AGENTS.md §2 non-negotiables verified <!-- id: audit-agents-rules -->
  - [x] .agents/rules.md stack and style guidelines verified <!-- id: audit-project-rules -->
- Schema compliance check:
  - [x] Conformity with .agents/schema.md verified <!-- id: audit-schema-conformity -->
