# Antigravity Agent Core (AAC) reproducible Windows installer.
# Usage: iwr -useb https://raw.githubusercontent.com/rafaelghifari/antigravity-agents/v4.3.5/install.ps1 | iex

$ErrorActionPreference = "Stop"
$AacRef = "v4.3.5"
$Repository = "https://github.com/rafaelghif/antigravity-agents.git"
$TargetDir = if ($env:AAC_TARGET_DIR) { $env:AAC_TARGET_DIR } else { (Get-Location).Path }
$TmpDir = Join-Path $env:TEMP ([System.Guid]::NewGuid().ToString())
$BackupDir = Join-Path $TargetDir (".agents-backups\" + (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ"))

function Copy-ManagedFile($Source, $RelativeDestination) {
    $Destination = Join-Path $TargetDir $RelativeDestination
    if (Test-Path $Destination) {
        $BackupDestination = Join-Path $BackupDir $RelativeDestination
        New-Item -ItemType Directory -Force -Path (Split-Path $BackupDestination) | Out-Null
        Copy-Item $Destination $BackupDestination -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path (Split-Path $Destination) | Out-Null
    if (Test-Path $Source -PathType Container) {
        New-Item -ItemType Directory -Force -Path $Destination | Out-Null
        Copy-Item (Join-Path $Source '*') $Destination -Recurse -Force
    } else {
        Copy-Item $Source $Destination -Force
    }
}

try {
    New-Item -ItemType Directory -Force -Path "$TargetDir\.agents\brain", "$TargetDir\.agents\common", "$TargetDir\.agents\incidents", "$TargetDir\.agents\locks", "$TargetDir\.agents\plans", "$TargetDir\.agents\scratch", "$TargetDir\.agents\skills", "$TargetDir\scripts" | Out-Null
    git clone --depth 1 --branch $AacRef $Repository $TmpDir | Out-Null
    python "$TmpDir\scripts\validate.py"

    Copy-ManagedFile "$TmpDir\AGENTS.md" "AGENTS.md"
    if (-not (Test-Path "$TargetDir\.env.example")) {
        Copy-Item "$TmpDir\.env.example" "$TargetDir\.env.example"
    }
    Copy-ManagedFile "$TmpDir\.agents\config.json" ".agents\config.json"
    Copy-ManagedFile "$TmpDir\.agents\TASK_TEMPLATE.md" ".agents\TASK_TEMPLATE.md"
    Copy-ManagedFile "$TmpDir\.agents\antigravity-settings.example.json" ".agents\antigravity-settings.example.json"
    Copy-ManagedFile "$TmpDir\.agents\antigravity-compatibility.json" ".agents\antigravity-compatibility.json"
    Copy-ManagedFile "$TmpDir\.agents\mcp_config.json.example" ".agents\mcp_config.json.example"
    Copy-ManagedFile "$TmpDir\.agents\brain" ".agents\brain"
    Copy-ManagedFile "$TmpDir\.agents\common" ".agents\common"
    Copy-ManagedFile "$TmpDir\.agents\skills" ".agents\skills"
    Copy-ManagedFile "$TmpDir\scripts\validate.py" "scripts\validate.py"
    Write-Host "AAC $AacRef installed into $TargetDir"
    Write-Host "Copy .agents\antigravity-settings.example.json into the global Antigravity CLI settings profile."
}
finally {
    if (Test-Path $TmpDir) { Remove-Item $TmpDir -Recurse -Force }
}
