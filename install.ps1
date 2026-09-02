# Antigravity Agent Core (AAC) reproducible Windows installer & upgrader.
# Usage: iwr -useb https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/install.ps1 | iex

$ErrorActionPreference = "Stop"
$Repository = "https://github.com/rafaelghif/antigravity-agents.git"
if (-not $AacRef) {
    try {
        $tags = (git ls-remote --tags --refs $Repository 2>$null | ForEach-Object { $_.Split('/')[-1] })
        $latest = $tags | Where-Object { $_ -match '^v?\d+\.\d+\.\d+' } | Sort-Object { [version]($_ -replace '^v','') } | Select-Object -Last 1
        $AacRef = if ($latest) { $latest } else { "v4.41.0" }
    } catch {
        $AacRef = "v4.41.0"
    }
}
$TargetDir = if ($env:AAC_TARGET_DIR) { $env:AAC_TARGET_DIR } else { (Get-Location).Path }
$TmpDir = Join-Path $env:TEMP ([System.Guid]::NewGuid().ToString())
$SourceDir = Join-Path $TmpDir "source"
$BackupStore = Join-Path $TmpDir "brain_backup"
$BackupDir = Join-Path $TargetDir (".agents-backups/" + (Get-Date).ToUniversalTime().ToString("yyyyMMddTHHmmssZ"))

if (-not (Get-Command git -ErrorAction SilentlyContinue)) { throw "Required command not found: git" }
if (-not (Get-Command curl -ErrorAction SilentlyContinue)) { throw "Required command not found: curl" }
if (-not (Get-Command jq -ErrorAction SilentlyContinue)) { throw "Required command not found: jq" }
if (-not (Get-Command gh -ErrorAction SilentlyContinue)) { throw "Required command not found: gh" }

$PythonCmd = $null
foreach ($cmd in @("python3", "python", "py")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        $PythonCmd = $cmd
        break
    }
}
if (-not $PythonCmd) { throw "Required command not found: python (or python3/py)" }

function Copy-ManagedFile($Source, $RelativeDestination) {
    $Destination = Join-Path $TargetDir $RelativeDestination
    if (Test-Path -LiteralPath $Destination) {
        $BackupDestination = Join-Path $BackupDir $RelativeDestination
        $BackupParent = Split-Path $BackupDestination -Parent
        if ($BackupParent -and -not (Test-Path -LiteralPath $BackupParent)) {
            New-Item -ItemType Directory -Force -Path $BackupParent | Out-Null
        }
        Copy-Item -LiteralPath $Destination -Destination $BackupDestination -Recurse -Force
    }
    if (Test-Path -LiteralPath $Source -PathType Container) {
        if (-not (Test-Path -LiteralPath $Destination)) {
            New-Item -ItemType Directory -Force -Path $Destination | Out-Null
        }
        Get-ChildItem -LiteralPath $Source -Force | Copy-Item -Destination $Destination -Recurse -Force
    } else {
        $DestParent = Split-Path $Destination -Parent
        if ($DestParent -and -not (Test-Path -LiteralPath $DestParent)) {
            New-Item -ItemType Directory -Force -Path $DestParent | Out-Null
        }
        Copy-Item -LiteralPath $Source -Destination $Destination -Force
    }
}

try {
    New-Item -ItemType Directory -Force -Path "$TargetDir/.agents/incidents", "$TargetDir/.agents/locks", "$TargetDir/.agents/plans", "$TargetDir/.agents/scratch", "$TargetDir/scripts" | Out-Null
    New-Item -ItemType Directory -Force -Path $BackupStore | Out-Null
    
    if (Test-Path -LiteralPath "$TargetDir/.agents/config.json") {
        Write-Host "=> Initiating AAC Upgrade to $AacRef..."
    } else {
        Write-Host "=> Initiating AAC Clean Install of $AacRef..."
    }

    $BrainFiles = @("rules.md", "memory.md", "ANCHOR.md", "active_context.md", "soul.md", "schema.md")
    foreach ($file in $BrainFiles) {
        $srcPath = Join-Path "$TargetDir/.agents/brain" $file
        if (Test-Path -LiteralPath $srcPath) {
            Copy-Item -LiteralPath $srcPath -Destination (Join-Path $BackupStore "$file.bak") -Force
        }
    }

    git clone --depth 1 --branch $AacRef $Repository $SourceDir | Out-Null
    if ($LASTEXITCODE -ne 0) { throw "git clone failed" }
    
    & $PythonCmd "$SourceDir/scripts/validate.py"
    if ($LASTEXITCODE -ne 0) { throw "python validation failed" }

    Copy-ManagedFile "$SourceDir/AGENTS.md" "AGENTS.md"
    Copy-ManagedFile "$SourceDir/GEMINI.md" "GEMINI.md"
    if (-not (Test-Path -LiteralPath "$TargetDir/.env.example") -and (Test-Path -LiteralPath "$SourceDir/.env.example")) {
        Copy-Item -LiteralPath "$SourceDir/.env.example" -Destination "$TargetDir/.env.example"
    }
    Copy-ManagedFile "$SourceDir/.agents" ".agents"
    Copy-ManagedFile "$SourceDir/scripts" "scripts"

    # Ensure upstream GitHub Actions workflows do not pollute target project
    foreach ($wf in @("agent-gates.yml", "agentic-cicd.yml")) {
        $wfPath = Join-Path "$TargetDir/.github/workflows" $wf
        if (Test-Path -LiteralPath $wfPath) {
            Remove-Item -LiteralPath $wfPath -Force
        }
    }
    $ghWfDir = Join-Path "$TargetDir/.github" "workflows"
    if ((Test-Path -LiteralPath $ghWfDir) -and ((Get-ChildItem -LiteralPath $ghWfDir -Force | Measure-Object).Count -eq 0)) {
        Remove-Item -LiteralPath $ghWfDir -Force
    }
    $ghDir = Join-Path "$TargetDir" ".github"
    if ((Test-Path -LiteralPath $ghDir) -and ((Get-ChildItem -LiteralPath $ghDir -Force | Measure-Object).Count -eq 0)) {
        Remove-Item -LiteralPath $ghDir -Force
    }

    foreach ($file in $BrainFiles) {
        $bakPath = Join-Path $BackupStore "$file.bak"
        if (Test-Path -LiteralPath $bakPath) {
            Copy-Item -LiteralPath $bakPath -Destination (Join-Path "$TargetDir/.agents/brain" $file) -Force
        }
    }

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
