# Antigravity Agent Core (AAC) V2 🚀

A project-agnostic, enterprise-grade developer protocol and operational workspace layout designed to standardize AI coding assistants (like Gemini, Claude, Cursor, Aider, and GPT-4) across **any** tech stack.

AAC V2 optimizes prompt caching, prevents secrets leakage, enforces architectural insulation, and dynamically auto-adapts to your project's programming languages and tools.

---

## 🌟 Supported Stacks (Stack-Agnostic)

AAC V2's auto-reconnaissance engine dynamically scans your repository and configures rules, schemas, and build/test environments for:
- **Node.js**: JavaScript, TypeScript, Next.js, React, Vue, NestJS, Express
- **PHP**: Core PHP, Laravel, WordPress
- **Python**: Python 3 standard, Pytest, Poetry, Pipenv
- **Go**: Golang modules and tooling
- **Rust**: Cargo suites
- **Java & Kotlin**: Maven and Gradle configurations
- **CSS / Styling**: Tailwind CSS, SCSS, Sass, Vanilla CSS
- **Mobile & Desktop**: .NET (C#)
- **Containerization**: Docker, Docker Compose

---

## 🚀 Getting Started (3-Step Setup)

To bootstrap your AI assistant in **any new or existing repository**:

### 1. Run the Installer
Run the bootstrap script inside your project's root folder:
```bash
curl -fsSL https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/bootstrap.sh | bash
```
*(Or copy the `bootstrap.sh` script to your local project root and run `bash bootstrap.sh`)*

### 2. Auto-Detect Your Stack
The installer automatically triggers the reconnaissance script (`.agents/scripts/recon.py`), which:
- Scans your project structure recursively.
- Replaces the placeholders in `AGENTS.md` with your detected languages and tools.
- Automatically writes test/build rules in `.agents/rules.md`.

### 3. Start Coding with the Agent
When prompting your agent, refer to the master instruction guidelines:
> "Read AGENTS.md and align with our workspace layout, rules, and memory ledger."

---

## 📂 The V2 Directory Blueprint

After running the bootstrap, your project will have the following layout:
- `AGENTS.md` (root): Master rules and directory maps loaded by the agent on every prompt.
- `.agents/rules.md`: Automatically generated build, test, and style configurations.
- `.agents/schema.md`: Holds definitions for config schemas and data formats.
- `.agents/tasks/board.md`: Active markdown task board for tracking progress.
- `.agents/memory/`:
  - `architecture.md`: High-level system architecture summary.
  - `decisions/`: Repository containing Architectural Decision Records (ADRs).
  - `glossary.md`: Key terms definitions.
  - `tech-debt.md` & `lessons-learned.md`: Logs for long-term project quality.
- `.agents/skills/`: Executable playbooks (e.g. `review/`, `debugging/`, `world-class-programmer/`).
- `.agents/workflows/`: Automation macros for shell slash commands.
