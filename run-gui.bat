@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%"

REM Always launch in STA mode so WPF works correctly
powershell -NoProfile -ExecutionPolicy Bypass -STA -File ".\gui-url-convert.ps1"

popd
pause