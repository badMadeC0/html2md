@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
echo [INFO] Script Directory: "%SCRIPT_DIR%"
if not exist "%SCRIPT_DIR%gui-url-convert.ps1" (
    echo [ERROR] File not found: "%SCRIPT_DIR%gui-url-convert.ps1"
    pause
    exit /b 1
)

REM Launch PowerShell with -File so script and argument paths are data, not code.
if "%~1"=="" (
    powershell -NoProfile -ExecutionPolicy Bypass -STA -File "%SCRIPT_DIR%gui-url-convert.ps1"
) else (
    echo [INFO] Batch processing file: "%~1"
    powershell -NoProfile -ExecutionPolicy Bypass -STA -File "%SCRIPT_DIR%gui-url-convert.ps1" -BatchFile "%~1"
)
pause
