# Antigravity Agent Core (AAC) reproducible Windows installer & upgrader.
# Usage: iwr -useb https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/install.ps1 | iex

$ErrorActionPreference = "Stop"
$Repository = "https://github.com/rafaelghif/antigravity-agents.git"
if (-not $AacRef) {
    try {
        $tags = (git ls-remote --tags --refs $Repository 2>$null | ForEach-Object { $_.Split('/')[-1] })
        $latest = $tags | Where-Object { $_ -match '^v?\d+\.\d+\.\d+' } | Sort-Object { [version]($_ -replace '^v','') } | Select-Object -Last 1
        $AacRef = if ($latest) { $latest } else { "v4.27.0" }
    } catch {
        $AacRef = "v4.27.0"
    }
}
$TargetDir = if ($env:AAC_TARGET_DIR) { $env:AAC_TARGET_DIR } else { (Get-Location).Path }
$TmpDir = Join-Path $env:TEMP ([System.Guid]::NewGuid().ToString())
$BackupDir = Join-Path $TargetDir (".agents-backups/" + (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ"))

if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "Required command not found: git" }
if (-not (Get-Command python -ErrorAction SilentlyContinue)) { throw "Required command not found: python" }

function Copy-ManagedFile($Source, $RelativeDestination) {
    $Destination = Join-Path $TargetDir $RelativeDestination
    if (Test-Path -LiteralPath $Destination) {
        $BackupDestination = Join-Path $BackupDir $RelativeDestination
        New-Item -ItemType Directory -Force -Path (Split-Path $BackupDestination) | Out-Null
        Copy-Item -LiteralPath $Destination -Destination $BackupDestination -Recurse -Force
    }
    New-Item -ItemType Directory -Force -Path (Split-Path $Destination) | Out-Null
    if (Test-Path -LiteralPath $Source -PathType Container) {
        New-Item -ItemType Directory -Force -Path $Destination | Out-Null
        Get-ChildItem -LiteralPath $Source | Copy-Item -Destination $Destination -Recurse -Force
    } else {
        Copy-Item -LiteralPath $Source -Destination $Destination -Force
    }
}

try {
    New-Item -ItemType Directory -Force -Path "$TargetDir/.agents/incidents", "$TargetDir/.agents/locks", "$TargetDir/.agents/plans", "$TargetDir/.agents/scratch", "$TargetDir/scripts" | Out-Null
    
    if (Test-Path -LiteralPath "$TargetDir/.agents/config.json") {
        Write-Host "=> Initiating AAC Upgrade to $AacRef..."
    } else {
        Write-Host "=> Initiating AAC Clean Install of $AacRef..."
    }

    $BrainFiles = @("rules.md", "memory.md", "ANCHOR.md")
    foreach ($file in $BrainFiles) {
        $srcPath = Join-Path "$TargetDir/.agents/brain" $file
        if (Test-Path -LiteralPath $srcPath) {
            Copy-Item -LiteralPath $srcPath -Destination (Join-Path $TmpDir "$file.bak") -Force
        }
    }

    git clone --depth 1 --branch $AacRef $Repository $TmpDir | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "git clone failed" }
    python "$TmpDir/scripts/validate.py"
    if ($LASTEXITCODE -ne 0) { throw "python validation failed" }

    Copy-ManagedFile "$TmpDir/AGENTS.md" "AGENTS.md"
    Copy-ManagedFile "$TmpDir/GEMINI.md" "GEMINI.md"
    if (-not (Test-Path -LiteralPath "$TargetDir/.env.example")) {
        Copy-Item -LiteralPath "$TmpDir/.env.example" -Destination "$TargetDir/.env.example"
    }
    Copy-ManagedFile "$TmpDir/.agents/config.json" ".agents/config.json"
    Copy-ManagedFile "$TmpDir/.agents/TASK_TEMPLATE.md" ".agents/TASK_TEMPLATE.md"
    Copy-ManagedFile "$TmpDir/.agents/antigravity-settings.example.json" ".agents/antigravity-settings.example.json"
    Copy-ManagedFile "$TmpDir/.agents/antigravity-compatibility.json" ".agents/antigravity-compatibility.json"
    Copy-ManagedFile "$TmpDir/.agents/mcp_config.json.example" ".agents/mcp_config.json.example"
    Copy-ManagedFile "$TmpDir/.agents/brain" ".agents/brain"

    foreach ($file in $BrainFiles) {
        $bakPath = Join-Path $TmpDir "$file.bak"
        if (Test-Path -LiteralPath $bakPath) {
            Copy-Item -LiteralPath $bakPath -Destination (Join-Path "$TargetDir/.agents/brain" $file) -Force
        }
    }

    Copy-ManagedFile "$TmpDir/.agents/common" ".agents/common"
    Copy-ManagedFile "$TmpDir/.agents/agents" ".agents/agents"
    Copy-ManagedFile "$TmpDir/.agents/skills" ".agents/skills"
    Copy-ManagedFile "$TmpDir/scripts/validate.py" "scripts/validate.py"
    Copy-ManagedFile "$TmpDir/scripts/verify.py" "scripts/verify.py"
    Copy-ManagedFile "$TmpDir/scripts/test_quality_guard.py" "scripts/test_quality_guard.py"
    Copy-ManagedFile "$TmpDir/scripts/semantic_grapher.py" "scripts/semantic_grapher.py"
    Copy-ManagedFile "$TmpDir/scripts/dry_guard.py" "scripts/dry_guard.py"
    Copy-ManagedFile "$TmpDir/scripts/git_hygiene_guard.py" "scripts/git_hygiene_guard.py"
    Copy-ManagedFile "$TmpDir/scripts/upgrade.py" "scripts/upgrade.py"
    Copy-ManagedFile "$TmpDir/scripts/ui_hygiene_guard.py" "scripts/ui_hygiene_guard.py"
    Copy-ManagedFile "$TmpDir/scripts/self_learner.py" "scripts/self_learner.py"
    Write-Host "AAC $AacRef successfully configured in $TargetDir"
    Write-Host "Copy .agents/antigravity-settings.example.json into the global Antigravity CLI settings profile."
}
catch {
    if (Test-Path -LiteralPath $BackupDir) { Get-ChildItem -LiteralPath $BackupDir | Copy-Item -Destination $TargetDir -Recurse -Force }
    throw
}
finally {
    if (Test-Path -LiteralPath $TmpDir) { Remove-Item -LiteralPath $TmpDir -Recurse -Force }
}
