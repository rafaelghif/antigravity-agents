---
name: test-driven-patch
description: Modifies codebase operations or fixes defects under strict TDD constraints inside specific application domains.
---

# Test-Driven Patching Skill

## 1. Input Specification
- **Requirements/Defect Report**: Detailed description of the target behavior or bug description.
- **Target Files**: List of production source code files to modify.
- **Test Files**: Target path of corresponding spec or test files.
- **Mock Context**: List of external dependencies (e.g. database connections, external APIs, security middleware) to mock.

## 2. Operational Procedures & Checklist
1. **Red Phase (Write and Fail)**:
   - Identify or create the test/spec file corresponding to the target feature.
   - Write a unit test simulating the input and asserting the correct behavior or bug resolution.
   - Run the test runner command for the target language (e.g., `npm run test -- <path>`, `go test`, `pytest <path>`, `cargo test`). Verify that the test fails with a deterministic, expected assertion error.
2. **Green Phase (Implement and Pass)**:
   - Navigate to the production file.
   - Write the minimum amount of production code required to satisfy the unit test requirements and make it pass.
   - Re-run the test runner. Ensure the test passes successfully without side effects.
3. **Refactor Phase (Clean and Standardize)**:
   - Clean up code styles: eliminate duplicate lines, improve variable naming, optimize loops, and apply architectural spacing standards.
   - Run the test runner once more to confirm the code remains green.
4. **Coverage Analysis**:
   - Run coverage analysis commands if available.
   - Ensure the new modules or lines added satisfy the project's coverage threshold (typically >= 90%).
5. **Regression Verification**:
   - Run the project's global test suite across the active folder to verify no existing tests are broken.

## 3. Decision Matrix
- **Are we testing controllers or services guarded by authentication headers?**
   - **YES**: Mock or bypass the authorization guards inside the test container setup or pass valid mock JWT headers in the HTTP request simulator.
- **Are we testing database repositories or DB operations?**
   - **YES**: Use standard mock/stub repository adapters or an in-memory database configuration (e.g. SQLite in-memory, Go-sqlmock, mockito) to isolate tests from local databases.
- **Are we testing UI views or native components?**
   - **YES**: Mock native plugins, browser globals, or HTTP fetch clients to ensure tests run completely sandbox-isolated.

## 4. Error Mitigation Tree
- **Test environment crashes due to missing configuration variables**:
   - *Mitigation*: Ensure mock variables are loaded inside the test configuration setup block, or pass them inline to the execution environment.
- **Flaky or timing-sensitive asynchronous tests**:
   - *Mitigation*: Avoid using arbitrary sleep timers. Use built-in testing library virtual clocks/fake timers or wait for promise/goroutine resolutions explicitly.

## 5. Output Verification Gate
- [ ] Unit/Integration tests run green locally.
- [ ] Modified or added lines achieve target code coverage thresholds.
- [ ] Global regression suite passes without regression errors.
