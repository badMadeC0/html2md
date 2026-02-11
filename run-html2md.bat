@echo off
setlocal
set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%"
if not exist ".venv\Scripts\python.exe" (
  echo [INFO] Creating virtual environment...
  py -3 -m venv ".venv" || python -m venv ".venv"
)
call ".venv\Scriptsctivate.bat"
REM Pass all args through to html2md
html2md %*
popd
