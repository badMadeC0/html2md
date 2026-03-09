for f in ["run-html2md.sh", "run-gui.sh"]:
    with open(f, "r") as file:
        content = file.read()

    old_block = '''# Install from cache purely offline
echo "[INFO] Installing package from local cache..."
if ! pip install html2md-cli --no-index --find-links="$CACHE_DIR" >/dev/null 2>&1; then
    echo "[ERROR] Failed to install from cache. The cache might be incomplete. Try deleting $CACHE_DIR and running again."
    e''' + '''xit 1
fi'''

    new_block = '''# Install from cache purely offline
echo "[INFO] Installing package from local cache..."
if ! pip install html2md-cli --no-index --find-links="$CACHE_DIR" >/dev/null 2>&1; then
    echo "[WARN] Failed to install from cache. The cache might be incomplete or for a different Python version."
    echo "[INFO] Attempting to rebuild wheels..."
    if ! pip wheel . -w "$CACHE_DIR"; then
        echo "[ERROR] Failed to build wheels. Check your internet connection or dependencies."
        e''' + '''xit 1
    fi
    echo "[INFO] Retrying installation..."
    if ! pip install html2md-cli --no-index --find-links="$CACHE_DIR" >/dev/null 2>&1; then
        echo "[ERROR] Failed to install even after rebuilding wheels."
        e''' + '''xit 1
    fi
fi'''

    content = content.replace(old_block, new_block)
    with open(f, "w") as file:
        file.write(content)

for f in ["run-html2md.bat", "run-gui.bat"]:
    with open(f, "r") as file:
        content = file.read()

    old_block_html2md = '''REM Install from cache purely offline
echo [INFO] Installing package from local cache...
pip install html2md-cli --no-index --find-links="!CACHE_DIR!" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to install from cache. The cache might be incomplete. Try deleting !CACHE_DIR! and running again.
    rmdir /s /q "!VENV_DIR!"
    popd
    e''' + '''xit /b 1
)'''

    new_block_html2md = '''REM Install from cache purely offline
echo [INFO] Installing package from local cache...
pip install html2md-cli --no-index --find-links="!CACHE_DIR!" >nul 2>&1
if errorlevel 1 (
    echo [WARN] Failed to install from cache. The cache might be incomplete or for a different Python version.
    echo [INFO] Attempting to rebuild wheels...
    pip wheel . -w "!CACHE_DIR!"
    if errorlevel 1 (
        echo [ERROR] Failed to build wheels. Check your internet connection or dependencies.
        rmdir /s /q "!VENV_DIR!"
        popd
        e''' + '''xit /b 1
    )
    echo [INFO] Retrying installation...
    pip install html2md-cli --no-index --find-links="!CACHE_DIR!" >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Failed to install even after rebuilding wheels.
        rmdir /s /q "!VENV_DIR!"
        popd
        e''' + '''xit /b 1
    )
)'''

    old_block_gui = '''REM Install from cache purely offline
echo [INFO] Installing package from local cache...
pip install html2md-cli --no-index --find-links="!CACHE_DIR!" >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Failed to install from cache. The cache might be incomplete. Try deleting !CACHE_DIR! and running again.
    rmdir /s /q "!VENV_DIR!"
    popd
    pause
    e''' + '''xit /b 1
)'''

    new_block_gui = '''REM Install from cache purely offline
echo [INFO] Installing package from local cache...
pip install html2md-cli --no-index --find-links="!CACHE_DIR!" >nul 2>&1
if errorlevel 1 (
    echo [WARN] Failed to install from cache. The cache might be incomplete or for a different Python version.
    echo [INFO] Attempting to rebuild wheels...
    pip wheel . -w "!CACHE_DIR!"
    if errorlevel 1 (
        echo [ERROR] Failed to build wheels. Check your internet connection or dependencies.
        rmdir /s /q "!VENV_DIR!"
        popd
        pause
        e''' + '''xit /b 1
    )
    echo [INFO] Retrying installation...
    pip install html2md-cli --no-index --find-links="!CACHE_DIR!" >nul 2>&1
    if errorlevel 1 (
        echo [ERROR] Failed to install even after rebuilding wheels.
        rmdir /s /q "!VENV_DIR!"
        popd
        pause
        e''' + '''xit /b 1
    )
)'''

    if f == "run-html2md.bat":
        content = content.replace(old_block_html2md, new_block_html2md)
    else:
        content = content.replace(old_block_gui, new_block_gui)

    with open(f, "w") as file:
        file.write(content)
