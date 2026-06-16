$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$helperPy = Join-Path $scriptPath "cli" "helper.py"

$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptPath)
$venvPython1 = Join-Path $projectRoot ".venv" "Scripts" "python.exe"
$venvPython2 = Join-Path $projectRoot ".venv" "bin" "python"
$venvPython3 = Join-Path $projectRoot ".venv" "bin" "python3"

$pyCmd = ""
if (Test-Path $venvPython1) {
    $pyCmd = $venvPython1
} elseif (Test-Path $venvPython2) {
    $pyCmd = $venvPython2
} elseif (Test-Path $venvPython3) {
    $pyCmd = $venvPython3
} else {
    # Fallback to system Python
    if (Get-Command python3 -ErrorAction SilentlyContinue) {
        $pyCmd = "python3"
    } elseif (Get-Command python -ErrorAction SilentlyContinue) {
        $pyVersion = & python -c 'import sys; print(sys.version_info[0])' 2>$null
        if ($pyVersion -eq "3") {
            $pyCmd = "python"
        } else {
            Write-Error "Error: Python 3 is required to run the Antigravity helper CLI. Please install Python 3 and ensure it is in your PATH."
            exit 1
        }
    } else {
        Write-Error "Error: Python 3 is required to run the Antigravity helper CLI. Please install Python 3 and ensure it is in your PATH."
        exit 1
    }
}

& $pyCmd $helperPy $args
