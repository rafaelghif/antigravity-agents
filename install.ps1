# Antigravity Agent Core (AAC) Universal Windows Bootstrap
# Delegates installation to cross-platform pure Python engine (install.py)
# Version marker for validation:
$AacRef = "v4.47.0"

# Enforce UTF-8 console, pipe, and process encoding across Windows
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::InputEncoding = [System.Text.Encoding]::UTF8
$env:PYTHONIOENCODING = "utf-8"
$env:PYTHONUTF8 = "1"

$Python = $null
foreach ($candidate in @("python3", "python", "py")) {
    $found = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($found) {
        $Python = $found.Source
        break
    }
}

if (-not $Python) {
    Write-Error "Error: Python 3 is required to install Antigravity Agent Core."
    exit 1
}

# If install.py is available locally, run it directly
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path -ErrorAction SilentlyContinue
if ($ScriptDir -and (Test-Path (Join-Path $ScriptDir "install.py"))) {
    & $Python (Join-Path $ScriptDir "install.py") $args
    exit $LASTEXITCODE
}

# Otherwise, download and run install.py directly
$TmpFile = [System.IO.Path]::GetTempFileName() + ".py"
Invoke-WebRequest -UseBasicParsing -Uri "https://raw.githubusercontent.com/rafaelghif/antigravity-agents/main/install.py" -OutFile $TmpFile
& $Python $TmpFile $args
$ret = $LASTEXITCODE
Remove-Item -Force $TmpFile -ErrorAction SilentlyContinue
exit $ret
