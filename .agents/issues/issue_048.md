---
id: issue-048
title: "Enforce strict security, exploit prevention, and code safety validation rules"
status: closed
assignee: agent-antigravity
created_at: 2026-06-27
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Prompt Engineering, Security Guidelines
- **Architecture**: Enforce a strict non-negotiable security and clean-code policy in `AGENTS.md` to prevent any possibility of vulnerabilities, unauthorized network access, obfuscated code, or exploit injection.
- **Key Modules**:
  - [AGENTS.md](file://./AGENTS.md)
  - [.agents/skills/security-audit/SKILL.md](file://./.agents/skills/security-audit/SKILL.md)

## 2. Implementation Subtasks
- [x] Acquire module locks for `bootstrap` <!-- id: subtask-locks -->
- [x] Append non-negotiable safety and exploit prevention rules to the rules list in `AGENTS.md` <!-- id: subtask-agents-rule -->
- [x] Update `security-audit/SKILL.md` to add explicit guidelines on exploit prevention, code transparency, and software supply chain security <!-- id: subtask-security-skill -->
- [x] Run validation, release locks, and merge cleanly <!-- id: subtask-finalize -->

## 3. Acceptance Criteria
- [x] Local tests and `./helper.sh validate` pass successfully
- [x] Clear security policies prohibiting obfuscation, backdoors, or malicious code injection exist in `AGENTS.md`
- [x] Explicit software supply chain and code transparency guidelines exist in `security-audit/SKILL.md`
