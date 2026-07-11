# Thin Bootstrapper delegate for Antigravity Agent Core (AAC) V3
$ErrorActionPreference = "Stop"

# 1. Prerequisite Check: Python 3 presence
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
    Write-Error "Error: Python 3 runtime is required to execute bootstrap."
    Exit 1
}

# 2. Delegate directly to the Python bootstrap command
& $PythonExec .agents/scripts/cli/helper.py bootstrap $args
