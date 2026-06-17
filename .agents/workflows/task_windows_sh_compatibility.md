# Task Workflow: Windows Shell Script Execution Compatibility

## 1. Scope & Objective
Fix Windows execution compatibility for shell scripts (`.sh` files) when `sh` is not in the system `PATH`. This ensures the CLI and its unit test suite run seamlessly on Windows systems with Git installed but not in the global environment PATH.

---

## 2. Design & Implementation Plan

### A. Locate `sh` Executable on Windows (`utils.py`)
Add a helper function `get_sh_executable()` in [utils.py](file:///D:/Muhammad%20Rafael%20Ghifari/Software%20Engineer/Application/antigravity-agents/.agents/scripts/cli/utils.py):
1. If not on Windows (`os.name != 'nt'`), return `'sh'`.
2. Check if `'sh'` is already in `PATH` using `shutil.which('sh')`.
3. If not found, run `git --exec-path` using `subprocess.run` to discover the Git installation root directory.
   - Parse the path (e.g., `C:\Program Files\Git\mingw64\libexec\git-core`).
   - Move up relative to that directory to check if `bin\sh.exe` or `usr\bin\sh.exe` exists under the Git root directory.
4. If still not found, check standard hardcoded Windows installation paths:
   - `C:\Program Files\Git\bin\sh.exe`
   - `C:\Program Files\Git\usr\bin\sh.exe`
   - `C:\Program Files (x86)\Git\bin\sh.exe`
5. Fallback to `'sh'`.

Update `run_shell_script` in `utils.py` to use `get_sh_executable()`.

### B. Update Unit Tests (`test_rotation.py`)
Import `utils` in `tests/test_rotation.py` and replace hardcoded `['sh', ...]` subprocess arguments with the resolved `get_sh_executable()` command.

### C. Standardize CLI Script Execution (`push.py`, `migrate.py`)
Modify `push.py` and `migrate.py` to execute helper scripts (`validate.sh` and `recon.sh`) using the unified `utils.run_shell_script()` helper instead of raw `subprocess.run()`.

### D. Scaffolded Test Alignment (`skills.py`)
Update the test template in `skills.py` to use `sys.executable` when calling Python scripts via `subprocess.run()` to prevent execution failures on Windows.

---

## 3. Verification & Testing Plan
- Run the test suite: `python tests/test_rotation.py`
- Verify all tests pass, including the API key rotation wrapper scripts and individual skill tests.
