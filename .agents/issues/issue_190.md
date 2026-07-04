---
id: issue-190
title: "Enforce programmatic rule audits and commit compliance headers"
status: open
assignee: agent-antigravity
created_at: 2026-07-04
---

# Issue Details

## Problem Statement
Enforce programmatic rule audits and commit compliance headers

## Tasks
- [ ] Add Compliance-Audit trailer line validation check to git commit-msg hook template <!-- id: task-commit-msg-compliance -->
- [ ] Add Compliance-Audit trailer line validation check to audit_commit_messages in validate.py <!-- id: task-validate-commit-msg -->
- [ ] Implement audit_codebase_rules_compliance to check for raw config file writes and duplicate inline shell templates <!-- id: task-codebase-rules-audit -->
- [ ] Update unit tests in test_validate.py to include Compliance-Audit in mocked commit messages <!-- id: task-test-compliance-trailer -->

## Acceptance Criteria
- [ ] The git commit-msg hook rejects commits lacking a Compliance-Audit: passed trailer.
- [ ] The validation guard rejects branches with commits lacking the Compliance-Audit: passed trailer.
- [ ] The codebase rule compliance check identifies raw writes to configuration files and inline shell templates.
