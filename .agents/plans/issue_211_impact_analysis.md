# Impact Analysis: Agent Identity Profile & Workspace Heartbeat Diagnostics

## 1. Explore Options

### Option A: Localized soul.md Persona & heartbeat Health-Check Command (Recommended)
* **Persona (`soul.md`)**: Create `.agents/memory/soul.md` to define identity (Antigravity CLI Agent Persona), core engineering philosophies (correctness, clean code, zero-touch autonomy), and collaboration guidelines.
* **Heartbeat Script (`heartbeat.py`)**: Create a script under commands to execute diagnostics on lock state validity, token budget remaining, hook integrity, and repository status, providing a fast "pulse check" of the agent's work environment.

### Option B: Rules-only Personality directive
* **Directive**: Place simple persona rules as rules inside `rules.md` without separating out file profiles or constructing a heartbeat command.

---

## 2. Trade-offs Matrix

| Criteria | Option A (Recommended) | Option B |
|---|---|---|
| **Identity Separation** | **High** (Separates stack rules from agent identity and personality profiles) | Low (Mixes personality directives with compiler rules) |
| **Workspace Health Diagnostics** | **High** (Heartbeat acts as a fast validation runner for lock and budget integrity) | None (Requires running the full validation guard) |
| **Maintainability** | **High** (Clearly defined registers under memory and scripts) | Medium (Grows the main rules file) |

---

## 3. Downstream Impacts
* **Diagnostics**: Developers can quickly check workspace health using `./helper.sh heartbeat`.
* **Identity**: The agent reads its `soul.md` profile to keep a consistent pairing persona.

---

## 4. Recommendation
Recommend **Option A** to implement both `soul.md` and `./helper.sh heartbeat`.
