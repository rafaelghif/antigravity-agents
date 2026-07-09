# Impact Analysis: Setup Wizard Integration in Bootstrap Shells

## 1. Explore Options

### Option A: Dispatch helper.py bootstrap inside Shell Scripts (Recommended)
* **Forwarding**: Add argument-forwarding dispatches at the tail of `bootstrap.sh` (`$@`) and `bootstrap.ps1` (`$args`) to run the Python setup wizard.
* **Benefits**: Single source of truth. Supports interactive wizards as well as non-interactive automated installs out-of-the-box.

### Option B: Rewrite Interactive Wizard Queries in Pure Bash / PowerShell
* **Scripting**: Implement `read -p` and `Read-Host` prompts, input validation, and regex replacement code inside the shell and PowerShell scripts.

---

## 2. Trade-offs Matrix

| Criteria | Option A (Recommended) | Option B |
|---|---|---|
| **DRY Compliance** | **High** (Reuses `bootstrap.py` questionnaire logic) | Low (Duplicates input prompts, file writes) |
| **Maintainability** | **High** (One central location for project stack templates) | Low (Requires updating three different files for any configuration changes) |
| **Windows Parity** | **High** (Python executes identically across both operating systems) | Medium (PowerShell code structures differ significantly from Bash) |

---

## 3. Downstream Impacts
* **Zero-Touch Setup**: Both the Windows and Linux installation flow will dynamically guide users through database/infrastructure queries in one execution loop.

---

## 4. Recommendation
Recommend **Option A**.
