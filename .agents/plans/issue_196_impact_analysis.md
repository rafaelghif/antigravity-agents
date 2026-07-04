# Pre-Implementation Impact Analysis — Issue-196

Evaluating approaches to dynamic workspace-isolated script execution in the MCP server.

## 1. Options Comparison

### Option A: Dynamic CWD-based Script Resolution (Recommended)
- **Description**: Resolve `token_cmd`, `lock_cmd`, and `validate_module` scripts dynamically based on `os.getcwd()/.agents/scripts`. Fall back to the globally registered script directory.
- **Complexity**: Low.
- **Maintainability**: High.
- **Performance**: High. Fully isolates execution to target project scripts (running target validation rules, lock budgets) without modifying global Cline settings.

### Option B: Workspace-Specific MCP Registry
- **Description**: Register a new MCP server configuration globally for each project workspace, named like `aac-v2-tools-<project-hash>`.
- **Complexity**: High. Requires continuous background daemon configurations and clutters Cline settings.

---

## 2. Recommendation
We recommend **Option A** because it is lightweight, completely transparent to the user, and immediately executes the target project's local code versions when tool calls are made.
