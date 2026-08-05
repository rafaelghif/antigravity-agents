# Antigravity Agent Core (AAC) reproducible Windows installer.
# Usage: iwr -useb https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/install.ps1 | iex

$ErrorActionPreference = "Stop"
$AacRef = "v4.3.4"
$Repository = "https://github.com/rafaelghif/antigravity-agents.git"
$TargetDir = if ($env:AAC_TARGET_DIR) { $env:AAC_TARGET_DIR } else { (Get-Location).Path }
$TmpDir = Join-Path $env:TEMP ([System.Guid]::NewGuid().ToString())
$BackupDir = Join-Path $TargetDir (".agents-backups\" + (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ"))

try {
    New-Item -ItemType Directory -Force -Path "$TargetDir\.agents\brain", "$TargetDir\.agents\common", "$TargetDir\.agents\incidents", "$TargetDir\.agents\locks", "$TargetDir\.agents\plans", "$TargetDir\.agents\scratch", "$TargetDir\.agents\skills", "$TargetDir\scripts" | Out-Null
    git clone --depth 1 --branch $AacRef $Repository $TmpDir | Out-Null

    if (Test-Path "$TargetDir\AGENTS.md") {
        New-Item -ItemType Directory -Force -Path $BackupDir | Out-Null
        Copy-Item "$TargetDir\AGENTS.md" "$BackupDir\AGENTS.md"
    }
    if (Test-Path "$TargetDir\.agents\config.json") {
        New-Item -ItemType Directory -Force -Path "$BackupDir\.agents" | Out-Null
        Copy-Item "$TargetDir\.agents\config.json" "$BackupDir\.agents\config.json"
    }

    Copy-Item "$TmpDir\AGENTS.md" "$TargetDir\AGENTS.md" -Force
    if (-not (Test-Path "$TargetDir\.env.example")) {
        Copy-Item "$TmpDir\.env.example" "$TargetDir\.env.example"
    }
    Copy-Item "$TmpDir\.agents\config.json", "$TmpDir\.agents\TASK_TEMPLATE.md", "$TmpDir\.agents\antigravity-settings.example.json", "$TmpDir\.agents\mcp_config.json.example" "$TargetDir\.agents" -Force
    Copy-Item "$TmpDir\.agents\brain\*" "$TargetDir\.agents\brain" -Recurse -Force
    Copy-Item "$TmpDir\.agents\common\*" "$TargetDir\.agents\common" -Recurse -Force
    Copy-Item "$TmpDir\.agents\skills\*" "$TargetDir\.agents\skills" -Recurse -Force
    Copy-Item "$TmpDir\scripts\validate.py" "$TargetDir\scripts\validate.py" -Force

    if (Test-Path "$TargetDir\scripts\validate.py") {
        python "$TargetDir\scripts\validate.py"
    }
    Write-Host "AAC $AacRef installed into $TargetDir"
    Write-Host "Copy .agents\antigravity-settings.example.json into the global Antigravity CLI settings profile."
}
finally {
    if (Test-Path $TmpDir) { Remove-Item $TmpDir -Recurse -Force }
}
