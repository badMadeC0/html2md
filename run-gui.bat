@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
echo [INFO] Script Directory: "%SCRIPT_DIR%"
if not exist "%SCRIPT_DIR%gui-url-convert.ps1" (
    echo [ERROR] File not found: "%SCRIPT_DIR%gui-url-convert.ps1"
    pause
    exit /b 1
)

REM Launch PowerShell. Use Set-Location to handle paths with '&'.
powershell -NoProfile -ExecutionPolicy Bypass -STA -Command "Set-Location -LiteralPath '%SCRIPT_DIR%'; & '.\gui-url-convert.ps1'"
pause