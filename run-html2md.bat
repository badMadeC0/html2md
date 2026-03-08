@echo off
setlocal enabledelayedexpansion

set "SCRIPT_DIR=%~dp0"
pushd "%SCRIPT_DIR%"

REM Define Downloads path
if defined USERPROFILE (
    set "DL_DIR=%USERPROFILE%\Downloads"
) else (
    set "DL_DIR=%HOMEDRIVE%%HOMEPATH%\Downloads"
)

REM Define Cache and Venv paths
set "CACHE_DIR=!DL_DIR!\html2md-cache\wheels"
set "VENV_DIR=!DL_DIR!\html2md-venv-%RANDOM%"

echo [INFO] Using cache directory: !CACHE_DIR!
echo [INFO] Creating temporary virtual environment: !VENV_DIR!

REM Create the temporary virtual environment
py -3 -m venv "!VENV_DIR!" 2>nul || python -m venv "!VENV_DIR!"
if not exist "!VENV_DIR!\Scripts\python.exe" (
    echo [ERROR] Failed to create virtual environment.
    popd
    exit /b 1
)

call "!VENV_DIR!\Scripts\activate.bat"

REM Upgrade pip/wheel in the new venv (quietly)
python -m pip install --upgrade pip wheel >nul 2>&1

REM Check if cache needs to be populated
if not exist "!CACHE_DIR!\*" (
    echo [INFO] Cache is empty. Downloading and building wheels to !CACHE_DIR!...
    mkdir "!CACHE_DIR!" 2>nul
    pip wheel . -w "!CACHE_DIR!"
    if errorlevel 1 (
        echo [ERROR] Failed to build wheels. Check your internet connection or dependencies.
        rmdir /s /q "!VENV_DIR!"
        popd
        exit /b 1
    )
) else (
    echo [INFO] Found cached wheels in !CACHE_DIR!.
)

REM Install from cache purely offline
echo [INFO] Installing package from local cache...
pip install . --no-index --find-links="!CACHE_DIR!" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to install from cache. The cache might be incomplete. Try deleting !CACHE_DIR! and running again.
    rmdir /s /q "!VENV_DIR!"
    popd
    exit /b 1
)

REM Pass all args through to html2md
echo [INFO] Running html2md...
html2md %*

REM Cleanup
echo [INFO] Cleaning up temporary virtual environment...
call "!VENV_DIR!\Scripts\deactivate.bat" 2>nul
rmdir /s /q "!VENV_DIR!"

popd
