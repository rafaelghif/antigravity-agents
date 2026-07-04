# AAC V2 Critical Architectural & Performance Analysis

This report provides a critical, objective evaluation of the **Antigravity Agent Core (AAC) V2** system, its local dashboard, verification gates, and operational patterns.

---

## 1. Core Architectural Flaws & Design Gaps

### A. Git Repository Pollution & History Bloat
- **The Issue**: AAC stores all its operational metadata—including local task tracking specs (`.agents/issues/`), file locks (`.agents/locks.json`), context manifests (`.agents/active_context.md`), and system configs—directly inside the project's Git repository.
- **The Consequence**: Operational meta-logic is tightly coupled with functional source code, violating the separation of concerns. The Git history becomes cluttered with automated commits such as `chore(release): close issue-146` and version bumps, increasing index overhead and noise.

### B. Broken Concurrency Control (Git-Based Locking)
- **The Issue**: The system attempts to prevent concurrent modifications by writing module locks to a static file committed to Git (`.agents/locks.json`).
- **The Consequence**: Git is designed for distributed merge control, not for real-time transactional locking. If multiple developers or agents work concurrently, they will encounter constant merge conflicts on `locks.json`. True lock managers require memory-based keyspaces (e.g., Redis) or active databases.

### C. Severe Security Vulnerability (Supply-Chain Risk)
- **The Issue**: The auto-updater (`upgrade.py`) automatically fetches and checks out files from the source repository's `main`/`master` tracking branch on the local machine.
- **The Consequence**: Arbitrary checkouts are run in the background without user confirmation or cryptographic signature checks. If the source repository is compromised, malicious code will automatically execute on the developer's workstation upon the next CLI run.

### D. Arbitrary Rules Pruning
- **The Issue**: Learned rules inside `rules.md` are capped at exactly 5 synthesized guidelines to save prompt tokens.
- **The Consequence**: The sorting and clustering algorithms are subjective. High-priority lessons risk being deleted or archived to `lessons-archive.md`, causing rules leakage where critical project-specific constraints are forgotten by the agent over time.

---

## 2. Dashboard Technical Debt & Gaps

### A. Non-Production Server Stack
- **The Issue**: The dashboard is powered by Python's basic `http.server` combined with `ThreadingMixIn`.
- **The Consequence**: The server runs on unencrypted HTTP and lacks reverse-proxy configurations, CORS controls, rate-limiting, or session validation. If exposed on a public interface, it exposes the local filesystem (via static file routes) and sensitive keys to unauthorized network access.

### B. Monolithic Polling vs. Event-Driven Updates
- **The Issue**: The frontend (`app.js`) is a monolithic script managing state, API updates, and rendering. It polls `/api/status` every 500ms when validation is active.
- **The Consequence**: Frequent polling wastes local CPU cycles and file-descriptor reads on the server. Modern architectures leverage WebSockets or Server-Sent Events (SSE) for push notifications instead of continuous client polling.

### C. Silent Failure & Poor Recovery
- **The Issue**: When the dashboard server goes offline, the frontend handles fetch failures silently in console logs without showing offline alerts or toasts, leaving the user confused.

---

## 3. Validation Gates Friction (validate.py)

### A. Over-Constraint & Developer Resistance
- **The Issue**: The pre-commit gate enforces a strict policy requiring all checklist subtasks (`- [ ]`) in the active issue file to be fully checked off (`[x]`) before a commit is allowed.
- **The Consequence**: This creates high friction for human developers who need to make rapid hotfixes or refactorings, encouraging them to bypass compliance altogether using `AAC_BYPASS_COMPLIANCE=1` or `--no-verify`.

### B. Regex-Based Secret Scanning Fragility
- **The Issue**: Credentials scanning relies entirely on simple regular expressions.
- **The Consequence**: Basic regex flags generate high false-positive rates on variable definitions (e.g., `db_password = os.getenv("DB_PASS")`) while failing to identify complex entropy patterns or token configurations in unstructured text.

---

## 4. Comparative Evaluation: Why Use AAC V2?

### Why You SHOULD Use It (Pros)
1. **Low Prompt Token Consumption**: By pruning and compressing rules and ADRs into highly concise, local Markdown files, it avoids bloat and keeps context windows warm.
2. **Deterministic LLM Constraints**: Programmatic hook validation prevents AI agents from committing broken code, leaking secrets, or failing branch alignment protocols.
3. **High Portability**: The entire setup is committed to Git. Any new developer or agent clone instantly gains identical workspace guidelines and checks with zero local server configuration.
4. **Structured Self-Learning**: Programmatic post-mortems via `./helper.sh learn` translate real-time errors directly into project rules.

### Why You Should NOT Use It (Cons)
1. **Repository Noise**: Operational commits and metadata pollute your Git tree, causing merge friction.
2. **Developer Friction**: Overly strict gating slows down rapid developer prototyping and hotfixing.
3. **No True Concurrency Support**: Committed lockfiles fail under real-world, concurrent multi-developer pipelines.
4. **Supply-Chain Danger**: Unsigned background git checkouts pose significant security risks.
