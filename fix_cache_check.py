files = ["run-html2md.bat", "run-gui.bat"]
for f in files:
    with open(f, "r") as file:
        content = file.read()
    content = content.replace('if not exist "!CACHE_DIR!\\*"', 'if not exist "!CACHE_DIR!\\html2md_cli*.whl"')
    with open(f, "w") as file:
        file.write(content)

files = ["run-html2md.sh", "run-gui.sh"]
for f in files:
    with open(f, "r") as file:
        content = file.read()
    content = content.replace('if [ ! -d "$CACHE_DIR" ] || [ -z "$(ls -A "$CACHE_DIR")" ]; then', 'if [ ! -d "$CACHE_DIR" ] || ! ls "$CACHE_DIR"/html2md_cli*.whl >/dev/null 2>&1; then')
    with open(f, "w") as file:
        file.write(content)
