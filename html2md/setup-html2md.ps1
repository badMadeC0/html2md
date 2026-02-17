<# setup-html2md.ps1 (0.11.6) - complete package #>
[CmdletBinding()]
param ([switch]$Quiet)
Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
$scriptRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptRoot
function Write-Info([string]$Message){ Write-Host "[INFO ] $Message" -ForegroundColor Cyan }
function Write-Warn([string]$Message){ Write-Host "[WARN ] $Message" -ForegroundColor Yellow }
function Write-Error2([string]$Message){ Write-Host "[ERROR] $Message" -ForegroundColor Red }
function Test-Command([string]$Name){ Get-Command $Name -ErrorAction SilentlyContinue }
function Find-Python { if (Test-Command 'py') { try { & py -3 -V | Out-Null; return @{ Command='py'; Args=@('-3') } } catch {} } if (Test-Command 'python') { try { & python -V | Out-Null; return @{ Command='python'; Args=@() } } catch {} } return $null }
function Install-PythonIfMissing { $py = Find-Python; if ($py) { return $py } Write-Warn "Python not found. Attempting install via winget..."; if (-not (Test-Command 'winget')) { Write-Warn "winget not available. Install from https://www.python.org/downloads/windows/ (check 'Add Python to PATH'), then re-run."; throw "winget not available" }; $pkgId = 'Python.Python.3.11'; $wingetArgs = @('install','-e','--id',$pkgId,'--source','winget','--accept-source-agreements','--accept-package-agreements'); Write-Info "Running: winget $($wingetArgs -join ' ')"; winget @wingetArgs; Start-Sleep -Seconds 3; $py = Find-Python; if (-not $py) { Write-Error2 "Python still not found after install."; throw "Python not found post-install" }; return $py }
function Add-PathIfMissing([string]$dir) { if (-not (Test-Path $dir)) { return } $userPath = [Environment]::GetEnvironmentVariable('Path','User'); $parts = $userPath -split ';' | Where-Object { $_ -ne '' }; if ($parts -notcontains $dir) { [Environment]::SetEnvironmentVariable('Path', ($userPath + ';' + $dir).Trim(';'), 'User'); Write-Info "Added to User PATH: $dir"; $script:PathAdjusted = $true } }
function Update-PythonPath { $roots = @("$env:LocalAppData\Programs\Python","$env:ProgramFiles\Python","$env:ProgramFiles(x86)\Python") | Where-Object { Test-Path $_ }; foreach ($r in $roots) { Get-ChildItem -Path $r -Directory -ErrorAction SilentlyContinue | ForEach-Object { $d = $_.FullName; Add-PathIfMissing $d; Add-PathIfMissing (Join-Path $d 'Scripts') } } }
try { Write-Info "Starting setup in: $scriptRoot"; try { Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force } catch {}; $py = Install-PythonIfMissing; Write-Info "Using Python command: $($py.Command) $($py.Args -join ' ')"; $script:PathAdjusted = $false; Update-PythonPath; if ($PathAdjusted -and -not $Quiet){ Write-Warn 'User PATH updated. Open a NEW PowerShell window for changes to apply.' }
 if (-not (Test-Path '.\.venv\Scripts\python.exe')){ Write-Info 'Creating virtual environment (.venv)...'; & $py.Command @($py.Args + @('-m','venv','.venv')) } else { Write-Info '.venv already exists.' }
 $pip = '.\.venv\Scripts\pip.exe'; if (-not (Test-Path $pip)){ Write-Error2 'pip not found in .venv'; throw 'venv pip missing' }
 Write-Info 'Upgrading pip/wheel/setuptools...'; & $pip install --upgrade pip wheel setuptools
 Write-Info 'Installing package in editable mode...'; & $pip install -e .
 $bat = Join-Path $scriptRoot 'run-html2md.bat'; $batLines = @('@echo off','setlocal','set "SCRIPT_DIR=%~dp0"','pushd "%SCRIPT_DIR%"','if not exist ".venv\Scripts\python.exe" (','  echo [INFO] Creating virtual environment...','  py -3 -m venv ".venv" || python -m venv ".venv"',')','call ".venv\Scripts\activate.bat"','REM Pass all args through to html2md','html2md %*','popd'); $batLines | Set-Content -Path $bat -Encoding ASCII; Write-Info "Created launcher: $bat"; Write-Host ''; Write-Host '✔ Setup complete.' -ForegroundColor Green; Write-Host 'You can now run:' -ForegroundColor Green; Write-Host '  .\run-html2md.bat --help' -ForegroundColor Green; Write-Host '' }
catch { Write-Error2 $_.Exception.Message; exit 1 }