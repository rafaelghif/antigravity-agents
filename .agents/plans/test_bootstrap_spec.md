# Pre-Implementation Impact Analysis

## Issue ID: issue-033
## Title: Implement comprehensive integration test suite for project bootstrap commands

This analysis compares two implementation options for the bootstrap test suite.

---

### Option A: Real File System Integration Testing using `tempfile.mkdtemp` (Recommended)
This option creates a test class `TestBootstrapCommand` in `.agents/tests/test_bootstrap.py` that utilizes a temporary directory to run `bootstrap.run(...)` programmatically. It verifies the existence and content of the generated files and folders.

#### Scenarios:
1. **Clean Architecture + Python**: Verifies `src/core/entities/`, `src/core/usecases/`, `requirements.txt`, `.gitignore`, `AGENTS.md`.
2. **Layered Architecture + Node**: Verifies `src/api/`, `src/services/`, `package.json`, etc.
3. **MVC Architecture + PHP**: Verifies `src/models/`, `src/views/`, `composer.json`, etc.
4. **Core File Copy**: Verifies `helper.sh`, `.agents/skills` copy logic.
5. **Invalid Arguments**: Verifies parameter boundaries (`sys.exit` triggers).

#### Pros:
- 100% realistic coverage of actual file output and bootstrap copying behaviors.
- Extremely robust.

#### Cons:
- Slower than pure mock testing due to disk I/O, but still runs in milliseconds.

---

### Option B: Full System Mocking via `unittest.mock.patch`
This option mocks all filesystem calls (`os.makedirs`, `open`, `shutil.copytree`, `shutil.copy2`) to prevent any disk writing.

#### Pros:
- Fast in-memory execution.

#### Cons:
- Extremely fragile: changes to folder walking or copying paths will break tests immediately.
- Mocking complex nested calls (like recursive folder traversal) is difficult to implement and maintain.

---

### Recommendation
**Option A** is the recommended choice. Using a real temporary directory ensures the bootstrapper's file copy and schema generation logic is 100% correct and matches production execution exactly.
