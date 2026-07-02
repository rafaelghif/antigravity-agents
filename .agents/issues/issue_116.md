---
id: issue-116
title: "Implement enterprise guardrails: GitHub Action template, active token context archiver, and README marketing pitch rewrite"
status: closed
assignee: agent-antigravity
created_at: 2026-07-02
---

# Issue Details

## Problem Statement
Implement enterprise guardrails: GitHub Action template, active token context archiver, and README marketing pitch rewrite

## Tasks
- [x] Create GitHub Action workflow template .agents/templates/github-action.yml and expose in installer/docs
- [x] Implement active context pruner archive logic in .agents/scripts/cli/commands/context.py to prune done tasks and issues
- [x] Rewrite README.md with the new marketing pitch ("Enterprise Guardrails for AI Coders")
- [x] Verify validations pass and close task

## Acceptance Criteria
- [x] GitHub Action workflow template is created and documented.
- [x] running ./helper.sh context optimize archives completed tasks to .agents/archive/ and updates .antigravityignore.
- [x] README.md clearly pitches the agent framework as guardrails for AI coding assistants.
- [x] Local validation guard passes cleanly.
