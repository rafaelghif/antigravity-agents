# Windows PowerShell Installer for Antigravity Agent Core (AAC) V2
param(
    [string]$TargetDir = "."
)

# Enable strict mode and stop on error
$ErrorActionPreference = "Stop"

$TargetAbs = [System.IO.Path]::GetFullPath((Join-Path (Get-Location) $TargetDir))

# 0. Check for Git presence
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "==========================================================" -ForegroundColor Red
    Write-Host "   [ERROR] Git is not installed!" -ForegroundColor Red
    Write-Host "==========================================================" -ForegroundColor Red
    Write-Host "Git is required to pull repository data, rotate profiles, and track version control."
    Write-Host "Please install Git (from https://git-scm.com) and run the installer again."
    Write-Host "Installation aborted."
    Write-Host "==========================================================" -ForegroundColor Red
    Exit 1
}

# 0. Check for Python 3 presence
$PythonExec = ""
$OldPreference = $ErrorActionPreference
$ErrorActionPreference = "SilentlyContinue"
try {
    if (Get-Command python -ErrorAction SilentlyContinue) {
        $Version = [string](& python --version 2>&1)
        if ($Version -match "Python 3") {
            $PythonExec = "python"
        }
    }
    if (-not $PythonExec -and (Get-Command python3 -ErrorAction SilentlyContinue)) {
        $Version = [string](& python3 --version 2>&1)
        if ($Version -match "Python 3") {
            $PythonExec = "python3"
        }
    }
} catch {}
$ErrorActionPreference = $OldPreference

if (-not $PythonExec) {
    Write-Host "==========================================================" -ForegroundColor Red
    Write-Host "   [ERROR] Python 3 is not installed!" -ForegroundColor Red
    Write-Host "==========================================================" -ForegroundColor Red
    Write-Host "Python 3 is required to run the Antigravity Agent Core CLI and validation hooks."
    Write-Host "If you do not install Python 3, the agent cannot function."
    Write-Host "Please install Python 3 (from https://www.python.org) and run the installer again."
    Write-Host "Installation aborted."
    Write-Host "==========================================================" -ForegroundColor Red
    Exit 1
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "   Installing Antigravity Agent Core V2..." -ForegroundColor Cyan
Write-Host "   Target Directory: $TargetAbs" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Verify target directory and backup existing installation for upgrade
if (-not (Test-Path $TargetAbs)) {
    New-Item -ItemType Directory -Force -Path $TargetAbs | Out-Null
}

$Timestamp = ""
$AgentsDir = Join-Path $TargetAbs ".agents"
$Agentsmd = Join-Path $TargetAbs "AGENTS.md"

if (Test-Path $AgentsDir) {
    $Timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $BackupDir = Join-Path $TargetAbs ".agents_backup_$Timestamp"
    Write-Host "Existing installation found! Archiving to .agents_backup_$Timestamp..."
    # Rename-Item can fail if target exists, force it
    Rename-Item -Path $AgentsDir -NewName ".agents_backup_$Timestamp" -Force
    
    if (Test-Path $Agentsmd) {
        Write-Host "Backing up AGENTS.md to AGENTS.md.backup_$Timestamp..."
        Copy-Item -Path $Agentsmd -Destination "$($Agentsmd).backup_$Timestamp" -Force | Out-Null
    }
}

# Get source path
$SrcDir = ""
if ($MyInvocation.MyCommand.Path) {
    $SrcDir = Split-Path $MyInvocation.MyCommand.Path -Parent
}

$LocalDev = $env:ANTIGRAVITY_LOCAL_DEV -eq "1"
$SrcAgents = Join-Path $SrcDir ".agents"

# 2. Copy/Download Agent files
Write-Host "Downloading Antigravity Agent Core from GitHub..."
    Write-Host "Verifying network connection to GitHub..."
    
    $Connected = $false
    try {
        $CheckConn = Invoke-WebRequest -Uri "https://github.com" -Method Head -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
        $Connected = $true
    } catch {
        try {
            $CheckConn = Invoke-WebRequest -Uri "https://github.com" -TimeoutSec 5 -UseBasicParsing -ErrorAction Stop
            $Connected = $true
        } catch {
            $Connected = $false
        }
    }
    
    if (-not $Connected) {
        Write-Host "==========================================================" -ForegroundColor Red
        Write-Host "   [ERROR] GitHub Connection Failed!" -ForegroundColor Red
        Write-Host "==========================================================" -ForegroundColor Red
        Write-Host "An active internet connection is required to download the Antigravity Agent Core"
        Write-Host "source files from GitHub."
        Write-Host "Please check your network connection and try again."
        Write-Host "Installation aborted."
        Write-Host "==========================================================" -ForegroundColor Red
        Exit 1
    }

    $TempDir = Join-Path $env:TEMP ([Guid]::NewGuid().ToString())
    New-Item -ItemType Directory -Force -Path $TempDir | Out-Null
    $ZipPath = Join-Path $TempDir "repo.zip"
    
    $RepoUrl = "https://github.com/rafaelghif/antigravity-agents/archive/refs/heads/main.zip"
    Write-Host "Downloading repository ZIP..."
    try {
        Invoke-WebRequest -Uri $RepoUrl -OutFile $ZipPath -UseBasicParsing -ErrorAction Stop
    } catch {
        Write-Host "Error: Failed to download repository ZIP from GitHub: $_" -ForegroundColor Red
        Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue | Out-Null
        Exit 1
    }
    
    Write-Host "Extracting repository ZIP..."
    try {
        Expand-Archive -Path $ZipPath -DestinationPath $TempDir -Force
    } catch {
        Write-Host "Error: Failed to extract repository ZIP: $_" -ForegroundColor Red
        Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue | Out-Null
        Exit 1
    }
    
    $ExtractedDirs = @(Get-ChildItem -Path $TempDir -Directory -Filter "antigravity-agents-*")
    if ($ExtractedDirs.Count -eq 0) {
        Write-Host "Error: Extracted repository folder not found." -ForegroundColor Red
        Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue | Out-Null
        Exit 1
    }
    $ExtractedDir = $ExtractedDirs[0].FullName
    
    if (-not (Test-Path (Join-Path $ExtractedDir ".agents"))) {
        Write-Host "Error: Extracted repository folder does not contain .agents directory." -ForegroundColor Red
        Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue | Out-Null
        Exit 1
    }
    
    Write-Host "Copying files to target directory..."
    $SrcAgents = Join-Path $ExtractedDir ".agents"
    $Files = Get-ChildItem -Path $SrcAgents -Recurse -File
    foreach ($File in $Files) {
        $RelativePath = $File.FullName.Substring($ExtractedDir.Length + 1)
        # Exclude specific files and directories (handling both slash directions)
        if ($RelativePath -like "*\__pycache__\*" -or $RelativePath -like "*/__pycache__/*" -or
            $RelativePath -like "*\.git\*" -or $RelativePath -like "*/.git/*" -or
            $File.Name -eq "git_profiles.json" -or
            $File.Name -eq "projects.json" -or
            $File.Name -eq "locks.json" -or
            $File.Name -eq "rules.md" -or
            $File.Name -eq ".DS_Store" -or
            $File.Extension -eq ".pyc" -or
            $File.Extension -eq ".pyo" -or
            $RelativePath -like ".agents\memory\*" -or $RelativePath -like ".agents/memory/*" -or
            $RelativePath -like ".agents\tasks\*" -or $RelativePath -like ".agents/tasks/*" -or
            $RelativePath -like ".agents\issues\*" -or $RelativePath -like ".agents/issues/*" -or
            $RelativePath -like ".agents\plans\*" -or $RelativePath -like ".agents/plans/*" -or
            $RelativePath -like ".agents\tests\*" -or $RelativePath -like ".agents/tests/*" -or
            $RelativePath -like ".agents\archive\*" -or $RelativePath -like ".agents/archive/*" -or
            $RelativePath -like ".agents\logs\*" -or $RelativePath -like ".agents/logs/*" -or
            $File.Name -eq "active_context.md" -or
            $File.Name -eq "token_budget.json" -or
            $File.Name -eq "sync_cache.json" -or
            $File.Name -eq "cooldowns.json" -or
            $File.Name -eq "upgrade_state.json" -or
            $File.Name -eq "schema.md" -or
            $File.Name -eq "api_keys" -or
            $File.Name -eq "active_api_keys" -or
            $File.Name -eq "active_api_keys.ps1" -or
            $File.Name -eq "active_api_profile_name") {
            continue
        }
        
        $DestFile = Join-Path $TargetAbs $RelativePath
        $DestDir = Split-Path $DestFile -Parent
        if (-not (Test-Path $DestDir)) {
            New-Item -ItemType Directory -Force -Path $DestDir | Out-Null
        }
        if (-not (Test-Path $DestFile)) {
            Copy-Item -Path $File.FullName -Destination $DestFile -Force | Out-Null
        }
    }
    
    # Initialize clean memory folder in target
    $DestMemory = Join-Path $TargetAbs ".agents\memory"
    $DestDecisions = Join-Path $DestMemory "decisions"
    $DestBlueprints = Join-Path $DestMemory "blueprints"
    
    if (-not (Test-Path $DestDecisions)) {
        New-Item -ItemType Directory -Force -Path $DestDecisions | Out-Null
    }
    if (-not (Test-Path $DestBlueprints)) {
        New-Item -ItemType Directory -Force -Path $DestBlueprints | Out-Null
    }
    
    $SrcBlueprints = Join-Path $ExtractedDir ".agents\memory\blueprints"
    if (Test-Path $SrcBlueprints) {
        Copy-Item -Path "$SrcBlueprints\*" -Destination $DestBlueprints -Recurse -Force -ErrorAction SilentlyContinue | Out-Null
    }
    
    $SrcTemplates = Join-Path $ExtractedDir ".agents\memory\templates"
    if (Test-Path $SrcTemplates) {
        $Templates = Get-ChildItem -Path $SrcTemplates -Filter "*.template"
        foreach ($T in $Templates) {
            $FilenameT = $T.BaseName
            $DestT = Join-Path $DestMemory $FilenameT
            if (-not (Test-Path $DestT)) {
                Copy-Item -Path $T.FullName -Destination $DestT -Force | Out-Null
            }
        }
    }

    # Copy projects.example to projects.json if it doesn't exist
    $SrcProjExample = Join-Path $ExtractedDir ".agents\projects.example"
    $DestProjJson = Join-Path $TargetAbs ".agents\projects.json"
    if ((Test-Path $SrcProjExample) -and -not (Test-Path $DestProjJson)) {
        Copy-Item -Path $SrcProjExample -Destination $DestProjJson -Force | Out-Null
    }

    $SrcHelperSh = Join-Path $ExtractedDir "helper.sh"
    $DestHelperSh = Join-Path $TargetAbs "helper.sh"
    if ((Test-Path $SrcHelperSh) -and -not (Test-Path $DestHelperSh)) {
        Copy-Item -Path $SrcHelperSh -Destination $DestHelperSh -Force | Out-Null
    }

    $SrcHelperPs = Join-Path $ExtractedDir "helper.ps1"
    $DestHelperPs = Join-Path $TargetAbs "helper.ps1"
    if ((Test-Path $SrcHelperPs) -and -not (Test-Path $DestHelperPs)) {
        Copy-Item -Path $SrcHelperPs -Destination $DestHelperPs -Force | Out-Null
    }
    
    $SrcAgentsMd = Join-Path $ExtractedDir "AGENTS.md"
    $DestAgentsMd = Join-Path $TargetAbs "AGENTS.md"
    if (-not (Test-Path $DestAgentsMd)) {
        Copy-Item -Path $SrcAgentsMd -Destination $DestAgentsMd -Force | Out-Null
        Write-Host "Created AGENTS.md."
    } else {
        Write-Host "AGENTS.md already exists. Skipping overwrite."
    }

    # Run bootstrap.ps1 from extracted folder inside target folder context
    $OriginalLocation = Get-Location
    Set-Location -Path $TargetAbs
    try {
        & (Join-Path $ExtractedDir "bootstrap.ps1")
    } finally {
        Set-Location -Path $OriginalLocation
    }
    
    # Cleanup
    Remove-Item -Path $TempDir -Recurse -Force -ErrorAction SilentlyContinue | Out-Null

# 3. Initialize Git if not present in target
if (-not (Test-Path (Join-Path $TargetAbs ".git"))) {
    Write-Host "Initializing empty Git repository in target directory..."
    git -C $TargetAbs init | Out-Null
}

# 4. Execute final synchronization in target directory
$OriginalLocation = Get-Location
Set-Location -Path $TargetAbs
try {
    & .\helper.ps1 sync
} finally {
    Set-Location -Path $OriginalLocation
}

if ($Timestamp) {
    Write-Host ""
    Write-Host "==========================================================" -ForegroundColor Yellow
    Write-Host "   [WARNING] Upgrade Backup Triggered!                    " -ForegroundColor Yellow
    Write-Host "==========================================================" -ForegroundColor Yellow
    Write-Host "Your old .agents config has been archived to:"
    Write-Host "  .agents_backup_$Timestamp"
    Write-Host "Your old AGENTS.md has been backed up to:"
    Write-Host "  AGENTS.md.backup_$Timestamp"
    Write-Host "To restore custom tasks, issues, or profiles, copy them"
    Write-Host "from the backup folder to the active .agents directory."
    Write-Host "==========================================================" -ForegroundColor Yellow
}

Write-Host "==========================================================" -ForegroundColor Green
Write-Host "   AAC V2 Installation Completed Successfully!            " -ForegroundColor Green
Write-Host "   Run './helper.ps1 validate' in the target folder to test." -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
