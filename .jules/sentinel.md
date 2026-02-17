## 2024-05-23 - Command Injection in PowerShell GUI
**Vulnerability:** `gui-url-convert.ps1` constructed `cmd.exe` command strings by interpolating user inputs (`$url` and `$outdir`) directly into arguments. This allowed command injection if inputs contained double quotes.
**Learning:** PowerShell's string interpolation does not automatically escape characters for `cmd.exe`. When invoking external processes, especially `cmd.exe /c`, inputs must be strictly validated or properly escaped.
**Prevention:** Use `Start-Process` with an argument list array where possible, or strictly validate/sanitize inputs to forbid dangerous characters like quotes before constructing command strings.
