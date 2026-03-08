with open("gui-url-convert.ps1", "r", encoding="utf-8") as f:
    content = f.read()

# Only run string replace ONCE for the main lines
content = content.replace('    $venvExe = Join-Path $scriptDir ".venv\\Scripts\\html2md.exe"\n    $pyScript = Join-Path $scriptDir "html2md.py"', '    $pyScript = Join-Path $scriptDir "html2md.py"\n    $html2mdCmd = Get-Command html2md -ErrorAction SilentlyContinue')

content = content.replace('        $venvExe = Join-Path $scriptDir ".venv\\Scripts\\html2md.exe"\n        $pyScript = Join-Path $scriptDir "html2md.py"', '        $pyScript = Join-Path $scriptDir "html2md.py"\n        $html2mdCmd = Get-Command html2md -ErrorAction SilentlyContinue')


content = content.replace('if (Test-Path -LiteralPath $venvExe) {\n                    & $venvExe $argsList', 'if ($html2mdCmd) {\n                    & $html2mdCmd.Source $argsList')
content = content.replace('Write-Error "Could not find html2md executable or script."', 'Write-Error "Could not find html2md command on PATH or html2md.py script."')

content = content.replace('if (Test-Path -LiteralPath $venvExe) {\n                    $output = & $venvExe $argsList 2>&1', 'if ($html2mdCmd) {\n                    $output = & $html2mdCmd.Source $argsList 2>&1')
content = content.replace('throw "Could not find html2md executable or script."', 'throw "Could not find html2md command on PATH or html2md.py script."')

with open("gui-url-convert.ps1", "w", encoding="utf-8") as f:
    f.write(content)
