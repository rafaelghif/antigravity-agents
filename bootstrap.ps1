# Bootstrap Antigravity Agent Core (AAC) V2 for Windows PowerShell
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Bootstrapping Antigravity Agent Core (AAC) V2...   " -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Create directories
$Dirs = @(
    ".agents/memory/decisions",
    ".agents/tasks",
    ".agents/issues",
    ".agents/skills/review",
    ".agents/skills/adr-writer",
    ".agents/skills/debugging",
    ".agents/skills/world-class-programmer",
    ".agents/workflows",
    ".agents/scripts"
)

foreach ($Dir in $Dirs) {
    if (-not (Test-Path $Dir)) {
        New-Item -ItemType Directory -Force -Path $Dir | Out-Null
    }
}

# 2. Write base files inline if they do not exist
if (-not (Test-Path "AGENTS.md")) {
    $AgentsContent = @"
# AGENTS.md — <Project Name>

> Antigravity CLI prepends this file to **every** prompt in this repo. Keep it short, factual, durable. Anything only *sometimes* relevant belongs in `.agents/skills/`, `.agents/memory/`, or `.agents/tasks/` and gets pulled in on demand.

## 1. What this project is
- **Product:** <one-line description>
- **Stack:** General Project
- **Repo layout:** Core CLI scripts, custom agent skills (`.agents/skills/`), workflows (`.agents/workflows/`), and project memory (`.agents/memory/`).

## 2. Non-negotiable rules
- **NEVER** commit secrets, `.env*` files, or credentials.
- **ALWAYS** run the project's test command before marking a task `Completed`.
- **ALWAYS** check `.agents/tasks/board.md` before starting work.
- **NEVER** create a new architectural decision without checking `.agents/memory/decisions/` first.

## 3. Context map — what loads when
| Path | Contents | When it loads |
|---|---|---|
| `AGENTS.md` (this file) | Identity, rules, map | Always |
| `.agents/skills/*/SKILL.md` | Playbooks | On demand |
| `.agents/tasks/board.md` | Task board | Read at start, written at change |
| `.agents/memory/architecture.md` | System summary | On demand |

## 4. Working protocol
1. **Before coding:** Read `.agents/tasks/board.md`.
2. **Before any architecture-affecting change:** check `.agents/memory/decisions/` for a relevant ADR.
"@
    Set-Content -Path "AGENTS.md" -Value $AgentsContent -Encoding UTF8
    Write-Host "Created AGENTS.md template."
}

if (-not (Test-Path ".agents/rules.md")) {
    $RulesContent = @"
# Project Rules
Use **General Project** for the main product stack.
- test command is: `N/A`.
"@
    Set-Content -Path ".agents/rules.md" -Value $RulesContent -Encoding UTF8
    Write-Host "Created .agents/rules.md template."
}

if (-not (Test-Path ".agents/tasks/board.md")) {
    $BoardContent = @"
# Task Board
## Todo
- [ ] Initialize project codebase
## Doing
## Done
"@
    Set-Content -Path ".agents/tasks/board.md" -Value $BoardContent -Encoding UTF8
    Write-Host "Created .agents/tasks/board.md template."
}

# 3. Trigger auto-reconnaissance
if (Get-Command python -ErrorAction SilentlyContinue) {
    python .agents/scripts/recon.py
} elseif (Get-Command python3 -ErrorAction SilentlyContinue) {
    python3 .agents/scripts/recon.py
} else {
    Write-Host "Warning: Python not found. Please run .agents/scripts/recon.py manually after installing Python." -ForegroundColor Yellow
}

# 4. Set up local Git hooks
if (Test-Path ".git") {
    $HookContent = @"
#!/usr/bin/env bash
if command -v python3 &>/dev/null; then
  python3 .agents/scripts/validate.py
elif command -v python &>/dev/null; then
  python .agents/scripts/validate.py
else
  echo "Warning: Python not found. Skipping commit validation check."
fi
"@
    Set-Content -Path ".git/hooks/pre-commit" -Value $HookContent -Encoding UTF8
    Write-Host "Installed local Git pre-commit hook."
}

Write-Host "==========================================================" -ForegroundColor Green
Write-Host "   AAC V2 Bootstrap Completed Successfully!             " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
