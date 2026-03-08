# Sentinel Journal

This journal records CRITICAL security learnings, vulnerabilities, and patterns found in the codebase.

## 2024-10-24 - CSV Injection in Log Export
**Vulnerability:** The `log_export.py` script directly wrote user-controlled input (JSON logs) to CSV without sanitization. If a log entry contained fields starting with `=`, `+`, `-`, or `@`, opening the CSV in Excel could execute arbitrary code (CSV Injection).
**Learning:** `csv.DictWriter` does not automatically sanitize fields for formula injection. Any tool exporting user data to CSV must explicitly sanitize formula triggers.
**Prevention:** Prefix any field value starting with `=`, `+`, `-`, or `@` with a single quote `'` to force it to be treated as text by spreadsheet applications.

## 2024-10-24 - Command Injection in PowerShell GUI
**Vulnerability:** `gui-url-convert.ps1` constructs a command string using unescaped user input (`$url` and `$outdir`) inside a single-quoted string context passed to `powershell -Command`. A malicious URL containing a single quote `'` allows arbitrary PowerShell code execution.
**Learning:** String concatenation for command construction is dangerous, even in PowerShell. Using `Start-Process -ArgumentList` with an array of arguments is safer than building a command string.
**Prevention:** Avoid `Invoke-Expression` or `powershell -Command "..."`. Use `& $exe $args` where `$args` is an array, or `Start-Process` with `ArgumentList`.

## 2024-10-24 - Terminal Injection in CLI
**Vulnerability:** The `cli.py` script directly printed exception messages using `print(f"Conversion failed: {e}")`. If the exception message contained terminal control characters (e.g., ANSI escape sequences `\x1b` or Bell `\x07`), it could allow an attacker to execute terminal injection attacks or manipulate the console output.
**Learning:** Terminal output from untrusted sources (including external HTTP responses that cause exceptions) must be sanitized before being displayed to the user.
**Prevention:** Sanitize exception messages or any untrusted output by filtering out non-printable characters, except for necessary whitespace like newlines and tabs. Example: `"".join(c for c in str(e) if c.isprintable() or c in "\n\t\r")`.
