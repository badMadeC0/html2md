import sys
import os

filepath = 'gui-url-convert.ps1'

with open(filepath, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False

for line in lines:
    # 1. Batch Mode Fix
    if '$psi.Arguments = "-NoExit -ExecutionPolicy Bypass -File `"$PSCommandPath`" -BatchFile `"$tempFile`" -BatchOutDir `"$outdir`""' in line:
        indent = line[:line.find('$psi')]
        new_lines.append(f'{indent}# Sanitize for double-quoted argument string (escape " with `")\n')
        new_lines.append(f'{indent}$safeOutDirBatch = $outdir -replace \'"\', \'`"\'\n')
        # Replace $outdir with $safeOutDirBatch
        line = line.replace('$outdir', '$safeOutDirBatch')
        new_lines.append(line)
        continue

    # 2. Single URL Mode Fix Setup
    # Hook into where $url is defined for single mode
    if '$url = $urlList[0]' in line:
        new_lines.append(line)
        indent = line[:line.find('$url')]
        new_lines.append(f'{indent}# Sanitize inputs for single-quoted command string (escape \' with \'\')\n')
        new_lines.append(f'{indent}$safeUrl = $url -replace "\'", "\'\'"\n')
        new_lines.append(f'{indent}$safeOutDir = $outdir -replace "\'", "\'\'"\n')
        continue

    # 3. Single URL Mode Fix Apply (venvExe case)
    if '$psi.Arguments = "-NoExit -Command `"& \'$venvExe\' --url \'$url\' --outdir \'$outdir\' --all-formats$optArg`""' in line:
        # Replace only the usages of variables inside the single quotes
        # careful not to replace other things.
        # Original: ... --url '$url' --outdir '$outdir' ...
        # New:      ... --url '$safeUrl' --outdir '$safeOutDir' ...
        line = line.replace("'$url'", "'$safeUrl'").replace("'$outdir'", "'$safeOutDir'")
        new_lines.append(line)
        continue

    # 4. Single URL Mode Fix Apply (pyScript case)
    if '$psi.Arguments = "-NoExit -Command `"& $pyCmd \'$pyScript\' --url \'$url\' --outdir \'$outdir\' --all-formats$optArg`""' in line:
        line = line.replace("'$url'", "'$safeUrl'").replace("'$outdir'", "'$safeOutDir'")
        new_lines.append(line)
        continue

    new_lines.append(line)

with open(filepath, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Fix applied successfully.")
