# Antigravity Agent Core (AAC) Windows PowerShell One-Line Installer Script
# Usage: Set-ExecutionPolicy Bypass -Scope Process -Force; iwr -useb https://raw.githubusercontent.com/rafaelghifari/antigravity-agents/main/install.ps1 | iex

$ErrorActionPreference = "Stop"

Write-Host "🚀 Installing Antigravity Agent Core (AAC) v4.3.0..." -ForegroundColor Cyan


# Create target directory structure
New-Item -ItemType Directory -Force -Path ".agents\brain\schemas" | Out-Null
New-Item -ItemType Directory -Force -Path ".agents\plans" | Out-Null
New-Item -ItemType Directory -Force -Path ".agents\incidents" | Out-Null
New-Item -ItemType Directory -Force -Path ".agents\scratch" | Out-Null
New-Item -ItemType Directory -Force -Path ".agents\skills" | Out-Null
New-Item -ItemType Directory -Force -Path ".agents\common" | Out-Null
New-Item -ItemType Directory -Force -Path ".agents\locks" | Out-Null

# Temporary clone directory
$TmpDir = Join-Path $env:TEMP ([System.Guid]::NewGuid().ToString())
git clone --depth 1 https://github.com/rafaelghifari/antigravity-agents.git $TmpDir | Out-Null

# Copy Core Directive and Configurations
Copy-Item -Path "$TmpDir\AGENTS.md" -Destination ".\AGENTS.md" -Force
Copy-Item -Path "$TmpDir\.agents\*" -Destination ".\.agents\" -Recurse -Force

# Copy default .env.example if missing
if (-not (Test-Path ".\.env.example")) {
    Copy-Item -Path "$TmpDir\.env.example" -Destination ".\.env.example" -Force
}

# Ensure clean template state for state.json (pure Mutex registry)
$StateFile = ".\.agents\brain\state.json"
$CleanState = @{
    claimed_tasks = @{}
    last_updated = (Get-Date -Format "o")
}
$CleanState | ConvertTo-Json -Depth 10 | Set-Content $StateFile

# Clean up temporary directory
Remove-Item -Path $TmpDir -Recurse -Force | Out-Null

Write-Host "✅ AAC v4.3.0 successfully installed into $((Get-Location).Path)!" -ForegroundColor Green
Write-Host "💡 Start your Antigravity CLI session (agy) to experience Task-Driven Zero-Amnesia autonomous coding." -ForegroundColor Yellow

