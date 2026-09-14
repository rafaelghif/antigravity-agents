# AAC (Antigravity Agent Core) Installer for Windows PowerShell
# Usage:
#   Local:  powershell -ExecutionPolicy Bypass -File install.ps1
#   Remote: irm https://raw.githubusercontent.com/rafaelghif/antigravity-agents-core/main/install.ps1 | iex

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$targetDir = Get-Location

Write-Host "`n🚀 Installing AAC (Antigravity Agent Core v5.0.2)..." -ForegroundColor Cyan
Write-Host "Target: $targetDir`n" -ForegroundColor Gray

$repoUrl = "https://github.com/rafaelghif/antigravity-agents-core/archive/refs/heads/main.zip"
$tempZip = Join-Path ([System.IO.Path]::GetTempPath()) "aac-main.zip"
$tempExtract = Join-Path ([System.IO.Path]::GetTempPath()) "aac-temp"

try {
    Write-Host "📥 Downloading framework archive from GitHub..." -ForegroundColor Yellow
    Invoke-WebRequest -Uri $repoUrl -OutFile $tempZip -UseBasicParsing

    if (Test-Path $tempExtract) {
        Remove-Item -Recurse -Force $tempExtract
    }

    Expand-Archive -Path $tempZip -DestinationPath $tempExtract -Force
    $sourceRoot = (Get-ChildItem -Directory -Path $tempExtract | Select-Object -First 1).FullName

    # 1. Copy .agents directory
    Write-Host "📦 Copying .agents/ (rules, skills, hooks, plugins)..." -ForegroundColor Yellow
    Copy-Item -Path (Join-Path $sourceRoot ".agents") -Destination $targetDir -Recurse -Force

    # 2. Copy docs directory (ADRs, tracker configs, templates)
    $sourceDocs = Join-Path $sourceRoot "docs"
    if (Test-Path $sourceDocs) {
        Write-Host "📚 Copying docs/ (ADRs, agents domain & tracker configs, templates)..." -ForegroundColor Yellow
        Copy-Item -Path $sourceDocs -Destination $targetDir -Recurse -Force
    }

    # 3. Copy root context and directives (NEVER COPY package.json)
    $rootFiles = @("AGENTS.md", "GEMINI.md", "CLAUDE.md", "CONTEXT.md", "skills-lock.json")
    foreach ($file in $rootFiles) {
        $src = Join-Path $sourceRoot $file
        $dst = Join-Path $targetDir $file
        if (Test-Path $src) {
            if (-not (Test-Path $dst)) {
                Copy-Item -Path $src -Destination $dst -Force
                Write-Host "📄 Created $file" -ForegroundColor Green
            } else {
                Write-Host "⏩ Skipped $file (already exists)" -ForegroundColor Gray
            }
        }
    }

    # 3. Create .scratch directory
    $scratchDir = Join-Path $targetDir ".scratch"
    if (-not (Test-Path $scratchDir)) {
        New-Item -ItemType Directory -Path $scratchDir -Force | Out-Null
        Set-Content -Path (Join-Path $scratchDir ".gitkeep") -Value "# Ephemeral scratchpad directory" -Force
        Write-Host "📁 Created .scratch/ directory" -ForegroundColor Green
    }

    # 4. Update .gitignore (never overwrite existing)
    $gitignorePath = Join-Path $targetDir ".gitignore"
    $rulesToAppend = @"

# Antigravity Runtime & Ephemeral State
.gemini/
*.log
*.tmp
.scratch/*
!.scratch/.gitkeep
handoff.md

# Credentials & MCP Secrets
.agents/mcp_config.json
!.agents/mcp_config.example.json
.agents/plugins/**/mcp_config.json
!.agents/plugins/**/mcp_config.example.json
"@

    if (Test-Path $gitignorePath) {
        $existing = Get-Content $gitignorePath -Raw
        if ($existing -notmatch "\.scratch/\*") {
            Add-Content -Path $gitignorePath -Value $rulesToAppend
            Write-Host "🛡️ Appended Antigravity guardrails to .gitignore" -ForegroundColor Green
        }
    } else {
        Set-Content -Path $gitignorePath -Value $rulesToAppend.Trim() -Force
        Write-Host "🛡️ Created .gitignore with Antigravity guardrails" -ForegroundColor Green
    }

    Write-Host "`n✅ Installation successful! (Zero package.json pollution)" -ForegroundColor Green
    Write-Host "👉 Open this repository in Antigravity IDE or Antigravity 2.0 to begin.`n" -ForegroundColor Cyan

} catch {
    Write-Host "❌ Installation failed: $_" -ForegroundColor Red
} finally {
    if (Test-Path $tempZip) { Remove-Item -Force $tempZip -ErrorAction SilentlyContinue }
    if (Test-Path $tempExtract) { Remove-Item -Recurse -Force $tempExtract -ErrorAction SilentlyContinue }
}
