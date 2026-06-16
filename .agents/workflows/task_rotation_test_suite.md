# Workflow Plan: Automated API Key Rotation Test Suite

This document defines the implementation details and plan for adding an automated test suite to verify the Bash and PowerShell API rotation wrappers.

---

## 1. Architectural Decisions

- **Single Cross-Platform Test Script (`tests/test_rotation.py`)**:
  - Implemented in Python for native cross-platform compatibility.
  - Temporarily backs up and restores the user's local API profile config files to avoid destructive actions.
  - Implements a `--mock-command` mode within the same script to simulate rate-limiting outputs.
- **Test Scenarios**:
  1. **Successful Rotation**: Verifies that the wrapper intercepts exit code 429, rotates from `mock_p1` to `mock_p2`, and succeeds.
  2. **Exhaustion Behavior**: Verifies that if all profiles return 429, the wrapper exits with the rate limit code after trying all profiles.
- **Integration**:
  - The test suite will be registered as a test check or command so it can be easily run.

---

## 2. Implementation Checklist

- [x] Create `tests/test_rotation.py` containing setup/teardown backup logic, `--mock-command` handling, and test assertions.
- [x] Add the test suite script to validation checks or run it to verify local wrapper functionality.
- [x] Document the test suite in `README.md` and `CHANGELOG.md`.
- [x] Verify validation checks pass and commit the changes.
- [x] Clean and release any locks.
