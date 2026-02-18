## 2024-05-23 - Command Injection in PowerShell GUI
**Vulnerability:** `gui-url-convert.ps1` constructed `cmd.exe` command strings by interpolating user inputs (`$url` and `$outdir`) directly into arguments. This allowed command injection if inputs contained double quotes.
**Learning:** PowerShell's string interpolation does not automatically escape characters for `cmd.exe`. When invoking external processes, especially `cmd.exe /c`, inputs must be strictly validated or properly escaped.
**Prevention:** Use `Start-Process` with an argument list array where possible, or strictly validate/sanitize inputs to forbid dangerous characters like quotes before constructing command strings.

## 2025-02-12 - CSV Injection in Log Export
**Vulnerability:** `html2md.log_export` directly exported JSONL logs to CSV without sanitizing fields starting with formula characters (`=`, `+`, `-`, `@`). This allowed malicious logs to execute arbitrary formulas when opened in spreadsheet software.
**Learning:** Simply dumping user-controlled data into CSV format can lead to formula injection (CSV injection). Data is not always safe just because it's text.
**Prevention:** Sanitize data exported to CSV by prepending a single quote `'` to fields starting with dangerous characters (`=`, `+`, `-`, `@`) to force them to be treated as text.
