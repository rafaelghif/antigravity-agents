# Thin Bootstrapper delegate for Antigravity Agent Core (AAC) V3
$ErrorActionPreference = "Stop"

# 1. Prerequisite Check: Check if standalone binary exists
$Arch = if ($env:PROCESSOR_ARCHITECTURE -eq "AMD64") { "x86_64" } else { $env:PROCESSOR_ARCHITECTURE }
$BinaryName = "agy-Windows-$Arch.exe"

if (Test-Path "bin\$BinaryName") {
    & "bin\$BinaryName" bootstrap $args
    Exit $LASTEXITCODE
}
if (Test-Path "$env:USERPROFILE\.local\bin\$BinaryName") {
    & "$env:USERPROFILE\.local\bin\$BinaryName" bootstrap $args
    Exit $LASTEXITCODE
}

# 2. Prerequisite Check: Python 3 presence
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
    Write-Error "Error: Standalone binary not found and Python 3 runtime is missing. Please download the compiled binary from GitHub Releases or install Python 3.8+."
    Exit 1
}

# 3. Delegate directly to the Python bootstrap command
& $PythonExec .agents/scripts/cli/helper.py bootstrap $args
