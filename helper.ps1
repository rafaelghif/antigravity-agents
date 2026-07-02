# Windows PowerShell wrapper for Antigravity Agent Core CLI

$ScriptDir = $PSScriptRoot
if (-not $ScriptDir) {
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
}
if (-not $ScriptDir) {
    $ScriptDir = Get-Location
}

$PythonExec = ""
if (Get-Command python -ErrorAction SilentlyContinue) {
    $Version = [string](& python --version 2>&1)
    if ($Version -match "Python 3") {
        $PythonExec = "python"
    }
}
if ((-not $PythonExec) -and (Get-Command python3 -ErrorAction SilentlyContinue)) {
    $Version = [string](& python3 --version 2>&1)
    if ($Version -match "Python 3") {
        $PythonExec = "python3"
    }
}

if ($PythonExec) {
    $HelperScript = Join-Path $ScriptDir ".agents/scripts/cli/helper.py"
    & $PythonExec $HelperScript @args
    exit $LASTEXITCODE
} else {
    Write-Error "Error: Python 3 runtime is required to execute Antigravity CLI commands."
    Exit 1
}
