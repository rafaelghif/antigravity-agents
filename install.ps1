# Windows PowerShell Installer for Antigravity Agent Core (AAC) V3
param(
    [string]$TargetDir = "."
)

$ErrorActionPreference = "Stop"

# 1. Prerequisite Check: Git presence
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Error "Error: Git is required to download/install Antigravity Agent Core."
    Exit 1
}

# 2. Clone source repository to a temp directory
$RepoUrl = $env:AAC_SOURCE_REPO
if (-not $RepoUrl) {
    $RepoUrl = "https://github.com/rafaelghif/antigravity-agents.git"
}

# Enforce online protocol check
$IsOnline = $false
foreach ($Proto in @("http://", "https://", "git@", "ssh://")) {
    if ($RepoUrl.StartsWith($Proto)) {
        $IsOnline = $true
        break
    }
}
if (-not $IsOnline) {
    $RepoUrl = "https://github.com/rafaelghif/antigravity-agents.git"
}

$TempPath = [System.IO.Path]::GetTempFileName()
Remove-Item $TempPath
New-Item -ItemType Directory -Path $TempPath | Out-Null

Write-Host "Fetching latest source core files..."
$OriginalEAP = $ErrorActionPreference
$ErrorActionPreference = "Continue"
& git clone --quiet --depth 1 $RepoUrl "$TempPath\repo" 2>$null
$ErrorActionPreference = $OriginalEAP
if ($LASTEXITCODE -ne 0) {
    Write-Error "Error: Failed to clone source repository from $RepoUrl."
    Exit 1
}

# 3. Check for standalone binary in the cloned repo
$Arch = if ($env:PROCESSOR_ARCHITECTURE -eq "AMD64") { "x86_64" } else { $env:PROCESSOR_ARCHITECTURE }
$BinaryName = "agy-Windows-$Arch.exe"

if (Test-Path "$TempPath\repo\bin\$BinaryName") {
    # 4a. Invoke standalone binary
    & "$TempPath\repo\bin\$BinaryName" install $TargetDir @args
} else {
    # 4b. Prerequisite Check: Python 3 presence and minimum version >= 3.8
    $PythonExec = ""
    try {
        if (Get-Command python -ErrorAction SilentlyContinue) {
            $Version = [string](& python --version 2>&1)
            if ($Version -match "Python 3") { $PythonExec = "python" }
        }
        if (-not $PythonExec -and (Get-Command python3 -ErrorAction SilentlyContinue)) {
            $Version = [string](& python3 --version 2>&1)
            if ($Version -match "Python 3") { $PythonExec = "python3" }
        }
    } catch {}

    if (-not $PythonExec) {
        Write-Error "Error: Standalone binary missing and Python 3.8 or newer is required to run Antigravity Agent Core."
        Exit 1
    }

    # Verify version
    $VersionString = & $PythonExec -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
    $VersionString = $VersionString.Trim()
    $Parts = $VersionString.Split('.')
    $Major = [int]$Parts[0]
    $Minor = [int]$Parts[1]
    if ($Major -lt 3 -or ($Major -eq 3 -and $Minor -lt 8)) {
        Write-Error "Error: Python 3.8 or newer is required. Found Python $VersionString."
        Exit 1
    }

    # Invoke the python unified installer from the cloned temp repository
    & $PythonExec "$TempPath\repo\.agents\scripts\cli\helper.py" install $TargetDir @args
}

# Cleanup
Remove-Item -Recurse -Force $TempPath -ErrorAction SilentlyContinue
