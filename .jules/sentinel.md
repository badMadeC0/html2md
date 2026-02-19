## 2024-05-22 - PowerShell Command Injection via String Interpolation
**Vulnerability:** Found a Command Injection vulnerability in `gui-url-convert.ps1` where user input was interpolated into a PowerShell command string executed via `-Command`.
**Learning:** PowerShell's `-Command` parameter executes a string as a script block. When constructing this string using variable interpolation (e.g., `"... '$url' ..."`), a single quote in the input can terminate the string literal and allow arbitrary command execution.
**Prevention:** Always escape single quotes in user input by doubling them (`.Replace("'", "''")`) when embedding values inside single-quoted strings in PowerShell commands. Additionally, sanitize inputs to remove illegal characters like double quotes in file paths.
