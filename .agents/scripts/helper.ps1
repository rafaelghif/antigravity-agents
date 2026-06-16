$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$helperPy = Join-Path $scriptPath "cli" "helper.py"

$pyCmd = "python3"
if (-not (Get-Command python3 -ErrorAction SilentlyContinue)) {
    if (Get-Command python -ErrorAction SilentlyContinue) {
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
