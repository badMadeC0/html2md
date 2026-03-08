for f in ["run-html2md.bat", "run-gui.bat"]:
    with open(f, "r", encoding="utf-8") as file:
        content = file.read()

    content = content.replace('    set "DL_DIR=%HOMEDRIVE%%HOMEPATH%\\Downloads"\n)', '    set "DL_DIR=%HOMEDRIVE%%HOMEPATH%\\Downloads"\n)\nmkdir "!DL_DIR!" 2>nul')

    with open(f, "w", encoding="utf-8") as file:
        file.write(content)

for f in ["run-html2md.sh", "run-gui.sh"]:
    with open(f, "r", encoding="utf-8") as file:
        content = file.read()

    content = content.replace('    fi\nfi\n', '    fi\nfi\nmkdir -p "$DL_DIR"\n')

    with open(f, "w", encoding="utf-8") as file:
        file.write(content)
