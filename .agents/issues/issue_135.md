---
id: issue-135
title: "Add lock compliance bypass switch for human developers"
status: open
assignee: agent-antigravity
created_at: 2026-07-02
---

# Design & Task Specification

## 1. Technical Decisions
- **Stack**: Python 3.
- **Architecture**: Precise bypass hook inside validation guard lock check module to ease developer workflow friction.
- **Key Modules**:
  - [.agents/scripts/validate.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/scripts/validate.py)
  - [.agents/tests/test_validate.py](file:///home/rafaelghifari/Muraghi/Project/antigravity-agent/.agents/tests/test_validate.py)

### Pre-Implementation Impact Analysis
- **Option A (Recommended)**: Introduce targeted bypass options (`SKIP_LOCK_AUDIT=true` or `AAC_BYPASS_LOCKS=1`) for the locking check.
  - *Trade-off*: Retains high security/safety (secrets check and test execution remain active) while alleviating locking constraints for rapid human development.
- **Option B**: Continue using global validation bypass (`AAC_BYPASS_COMPLIANCE=1`).
  - *Trade-off*: Promotes unsafe commits since developers must disable all tests and security audits to skip locking.

## 2. Implementation Subtasks
- [ ] Subtask 1: Add environment variable check at the top of `audit_module_locks()` in `validate.py`.
- [ ] Subtask 2: Add unit tests in `test_validate.py` covering the lock audit bypass behavior.
- [ ] Subtask 3: Verify all workspace tests and validation guards pass successfully.

## 3. Acceptance Criteria
- [ ] Setting `SKIP_LOCK_AUDIT=true` or `AAC_BYPASS_LOCKS=1` allows committing without locking files first.
- [ ] Unit tests for lock validation bypass return success.
- [ ] Validation suite passes without errors.
