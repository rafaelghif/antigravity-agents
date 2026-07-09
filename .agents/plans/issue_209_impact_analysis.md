# Impact Analysis: Proactive Prompt Looping & Zero-Touch Execution

## 1. Explore Options

### Option A: Proactive Checklist Execution Rules (Recommended)
* **Rules Update**: Enforce a "Self-Driving Agent" prompt rule inside `AGENTS.md` and project rules. The agent is instructed to dynamically parse its checklist, resolve the next logical step, and execute it immediately without asking the user or halting between tasks.
* **Simplification**: Replace lint-centric loop checking with functional checklist loop checking to reduce context tokens and emphasize step-by-step progress.

### Option B: Scripted CLI State Machine Wrapper
* **Script Wrapper**: Modify `./helper.sh` or create an interactive runner that parses `.agents/tasks/board.md` or the checklist and automatically feeds prompts to the agent sequentially.
* **Control**: Gives the human script control over task transitions.

---

## 2. Trade-offs Matrix

| Criteria | Option A (Recommended) | Option B |
|---|---|---|
| **User Friction** | **Zero** (Agent drives itself; zero-touch flow) | Medium (User still runs a script wrapper) |
| **Generality** | **High** (Applies to all clients like Cursor, Aider, Cline, agy) | Low (Only works inside standard terminal shells) |
| **Context footprint** | **Low** (Simple instructions in core prompt template) | Medium (Requires parsing logic scripts) |
| **Robustness** | **High** (Agent aligns internally on its checklist status) | Medium (Script can easily get out of sync if git branches change) |

---

## 3. Downstream Impacts
* **Self-Driving Compliance**: The agent will run faster and complete multiple subtasks in a single session invocation, significantly reducing developer effort.
* **Validation Hooks**: All changes still pass git hooks and unit validation cleanly.

---

## 4. Recommendation
Recommend **Option A**. It relies on high-quality prompt-level instructions in `AGENTS.md` to establish proactive self-driving looping, keeping operations completely zero-touch and hallucination-free.
