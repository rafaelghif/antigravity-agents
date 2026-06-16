$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
$helperPy = Join-Path $scriptPath "cli" "helper.py"
python3 $helperPy $args
