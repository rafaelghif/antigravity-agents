# Impact Analysis: Verification of Installer & Bootstrap Dependencies

## 1. Explore Options

### Option A: Integrate Verification Rules in Identity Profile & Rules (Recommended)
* **Rules Integration**: Update `soul.md`, `rules.md`, `rules.md.template`, and `AGENTS.md` with explicit non-negotiable rules.
* **Directives**:
  * **ALWAYS** trace dependencies between command scripts and shell wrappers.
  * **ALWAYS** audit installers (`install.sh`, `install.ps1`) and bootstrap scripts (`bootstrap.sh`, `bootstrap.ps1`) when changing CLI features or parameter signatures.
  * **ALWAYS** maintain a cohesive workspace file mapping.

### Option B: Hand-off verification manually
* **Action**: Do not update workspace rules; let the user manually double-check installers each time.

---

## 2. Trade-offs Matrix

| Criteria | Option A (Recommended) | Option B |
|---|---|---|
| **Rigor & Prevention** | **High** (Enforces prompt-level constraints on future agents) | Low (Dependent on manual verification) |
| **Workspace Consistency** | **High** (Keeps installer versions synced across Windows and Linux platforms) | Low (Platform parity might drift) |

---

## 3. Downstream Impacts
* **Parity**: Ensures Windows and Linux setup/bootstrap hooks remain 100% synchronized and tested.

---

## 4. Recommendation
Recommend **Option A**.
