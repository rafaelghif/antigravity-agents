# Windows PowerShell wrapper for Antigravity Agent Core CLI

$ScriptDir = $PSScriptRoot
if (-not $ScriptDir) {
    $ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
}
if (-not $ScriptDir) {
    $ScriptDir = Get-Location
}

$PythonExec = ""
if (Get-Command python3 -ErrorAction SilentlyContinue) {
    $PythonExec = "python3"
} elseif (Get-Command python -ErrorAction SilentlyContinue) {
    $PythonExec = "python"
}

if (-not $PythonExec) {
    Write-Host "[AAC HALT] CRITICAL ERROR: Python 3 runtime is required but not found on this system!" -ForegroundColor Red
    Write-Host "[AAC HALT] The agent MUST HALT execution immediately and inform the human to install Python 3." -ForegroundColor Red
    Exit 1
}

$PyCheck = & $PythonExec -c 'import sys; sys.exit(0 if sys.version_info >= (3, 8) else 1)' 2>$null
if ($LASTEXITCODE -ne 0) {
    $VerStr = & $PythonExec --version 2>&1
    Write-Host "[AAC HALT] CRITICAL ERROR: Python 3.8+ is required. Found: $VerStr" -ForegroundColor Red
    Write-Host "[AAC HALT] The agent MUST HALT execution immediately and inform the human to upgrade Python." -ForegroundColor Red
    Exit 1
}

$HelperScript = Join-Path $ScriptDir ".agents/scripts/cli/helper.py"
& $PythonExec $HelperScript @args
exit $LASTEXITCODE
