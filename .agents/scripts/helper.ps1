$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$helperPy = Join-Path (Join-Path $scriptPath "cli") "helper.py"

$projectRoot = Split-Path -Parent (Split-Path -Parent $scriptPath)
$venvPython1 = Join-Path (Join-Path (Join-Path $projectRoot ".venv") "Scripts") "python.exe"
$venvPython2 = Join-Path (Join-Path (Join-Path $projectRoot ".venv") "bin") "python"
$venvPython3 = Join-Path (Join-Path (Join-Path $projectRoot ".venv") "bin") "python3"

$pyCmd = ""
if (Test-Path $venvPython1) {
    $pyCmd = $venvPython1
} elseif (Test-Path $venvPython2) {
    $pyCmd = $venvPython2
} elseif (Test-Path $venvPython3) {
    $pyCmd = $venvPython3
} else {
    # Fallback to system Python, testing each command to ensure it's a real Python 3
    foreach ($cmd in @("python", "python3")) {
        if (Get-Command $cmd -ErrorAction SilentlyContinue) {
            $pyVersion = & $cmd -c 'import sys; print(sys.version_info[0])' 2>$null
            if ($pyVersion -eq "3") {
                $pyCmd = $cmd
                break
            }
        }
    }
    if (-not $pyCmd) {
        Write-Error "Error: Python 3 is required to run the Antigravity helper CLI. Please install Python 3 and ensure it is in your PATH."
        exit 1
    }
}

& $pyCmd $helperPy $args
