# Antigravity Agents Domain Context

Living domain document defining bounded contexts, core terminology, and architectural boundaries for the **antigravity-agents** workspace.

---

## 1. Domain Glossary

- **Antigravity (AGY)**: Google's agentic AI development platform supporting Antigravity IDE, Antigravity 2.0 desktop app, and Antigravity CLI (`agy`).
- **Gemini 3.8 Flash (High)**: The primary inference model powering the agent pair-programmer, optimized for speed, precision, and tool-augmented reasoning.
- **Skill**: On-demand procedural knowledge packaged in `.agents/skills/<name>/SKILL.md`. Leverages progressive disclosure: only name and description are exposed in context until activated via `view_file`.
- **Rule**: Behavioral constraints and operational policies. Root directives reside in `AGENTS.md`; modular rules reside in `.agents/rules/*.md` with `trigger: always_on` or `trigger: model_decision`.
- **Lifecycle Hook**: Event interceptors defined in `.agents/hooks.json` running at specific agent events (`PreToolUse`, `PostToolUse`, `PreInvocation`, `PostInvocation`, `Stop`).
- **Plugin**: Bundle of related skills, rules, and MCP configurations packaged under `.agents/plugins/<name>/plugin.json`.
- **Sidecar**: Autonomous diagnostic process declared in `.agents/plugins/**/sidecars/` that runs health checks and reports status without polluting main context.
- **Model Context Protocol (MCP)**: Tool integration standard providing external APIs (e.g. Gitea stdio, GitHub SSE) to agent context via project `.agents/mcp_config.json`.

---

## 2. Bounded Contexts & File Structure

```
D:\Project\antigravity-agents\
├── AGENTS.md                  # Root instructions (Highest workspace priority, <12k chars)
├── GEMINI.md                  # Pointer to AGENTS.md for compatibility
├── CONTEXT.md                 # Domain dictionary & architectural boundaries (this file)
├── .agents/                   # Workspace-scoped Antigravity configuration
│   ├── rules/                 # Modular always-on rules (caveman, ponytail, git, memory)
│   ├── skills/                # 64 on-demand progressive disclosure skills
│   ├── plugins/               # Workspace packaged plugins (workspace-integrations)
│   ├── hooks.json             # Lifecycle hook declarations (PreToolUse, etc.)
│   ├── plugins.json           # Explicit plugin manifest
│   ├── skills.json            # Explicit skill manifest
│   ├── mcp_config.json        # Project-scoped MCP tool config (gitignored)
│   └── mcp_config.example.json# Project-scoped MCP template (tracked)
├── docs/                      # Project documentation
│   ├── adr/                   # Architectural Decision Records (ADRs)
│   ├── agents/                # Agent skill configurations (issue tracker, domain, triage)
│   └── templates/             # Session handoff and reusable templates
└── .scratch/                  # Ephemeral working directory (gitignored)
    └── handoff.md             # Inter-session bridge handoff document
```

---

## 3. Communication & Code Contracts

1. **Caveman Principle**: Fluff-free, zero filler, immediate technical substance.
2. **Ponytail Ladder**: YAGNI -> Reuse -> Stdlib -> Platform -> Dependency -> One-Liner -> Minimal Diff.
3. **PowerShell Only**: Windows environment. Command chaining strictly via `;` (never `&&`).
4. **Clickable Links**: All file paths and symbols formatted as `[Label](file:///D:/Project/...)` with forward slashes.
