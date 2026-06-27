---
name: testing
description: Playbook for executing unit and integration tests, mocking external services, and structuring test suites.
---

# Testing & Test Automation Playbook

This playbook establishes the guidelines, strategies, and patterns for implementing testing and test automation at an enterprise scale, ensuring code safety, reliability, and zero-regression deployments without unnecessary overhead.

---

## 1. Test Categorization & Isolation

To maintain a fast and reliable CI/CD pipeline, tests are divided into two tiers (E2E testing is omitted to optimize token usage and avoid redundant runtime overhead):

### A. Unit Tests (Fast & Deterministic)
- **Scope**: Validate single functions, utility modules, or isolated classes.
- **Rules**:
  - Must run completely offline (no database, no external network, no file system read/write dependencies).
  - Use mocking or dependency injection to isolate the code under test.
  - Execution speed must be under 100ms per test.

### B. Integration Tests (Component Interoperability)
- **Scope**: Validate interactions between modules, database repositories, API clients, and services.
- **Rules**:
  - Network and database components may be active, but should preferably use local mocks or isolated databases (e.g., SQLite in-memory).
  - Maintain absolute cleanup (rollback database transactions or reset state) after each test run.

---

## 2. Mocking Guidelines & Best Practices

Mocking is essential for isolation, but over-mocking leads to fragile tests that fail to detect real integration bugs.

### A. What to Mock
- **External APIs**: Always mock HTTP calls to external vendors or web endpoints.
- **Timers and System Clocks**: Mock time dependencies to ensure consistency (e.g., testing token expiration).
- **Expensive Operations**: Mock heavy computational tasks or slow subprocesses.

### B. Mocking Patterns in Python (pytest / unittest.mock)
```python
from unittest.mock import patch, MagicMock

# Best Practice: Patch at the import location, not definition location
@patch('module_under_test.external_api_call')
def test_fetch_user_data(mock_api):
    # Setup mock return value
    mock_api.return_value = {"id": 1, "name": "John Doe"}
    
    result = module_under_test.get_user(1)
    
    assert result["name"] == "John Doe"
    mock_api.assert_called_once_with(1)
```

---

## 3. Test Organization & Conventions

To keep tests clean and maintainable:
- **Test Directory**: Place all tests in a `tests/` directory at the root of the project.
- **File Naming**: Name files with a `test_` prefix (e.g., `test_auth.py`, `test_utils.py`).
- **Test Cases**: Name test functions descriptively starting with `test_` followed by the action and expected behavior (e.g., `test_authenticate_with_invalid_credentials_fails`).
- **Assertive Assertions**: Use specific assertions and descriptive error messages rather than simple `assert True`.
