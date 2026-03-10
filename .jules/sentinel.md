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

## 2024-10-24 - Safe PowerShell String Interpolation
**Vulnerability:** Constructing PowerShell commands via string interpolation (e.g., `-Command "..."`) is risky. While `Start-Process -ArgumentList` is preferred, it may not support all use cases (like keeping the window open with `-NoExit` easily without wrapper scripts).
**Learning:** When using `-Command` is unavoidable, wrapping arguments in single quotes and escaping existing single quotes by doubling them (`' -> ''`) provides a robust defense against injection.
**Prevention:** Always sanitize variables before interpolating them into a command string. For single-quoted strings in PowerShell, replace `'` with `''`.


## 2024-10-24 - SSRF and Local File Inclusion (LFI) vulnerability
**Vulnerability:** The CLI tool accepts URL arguments to fetch and convert HTML content, but lacked validation, allowing users to provide `file://` or local IP URLs (e.g. `http://localhost`, `http://169.254.169.254/`). This exposed the application to SSRF (accessing internal cloud metadata or services) and LFI (reading arbitrary local files).
**Learning:** When building tools that fetch URLs, never blindly trust user input. Server-Side Request Forgery and Local File Inclusion are high-severity vulnerabilities common in fetchers or converters.
**Prevention:** Always validate URLs against a strict allowlist of schemes (`http`, `https`), ensure the hostname is not a loopback or private IP (e.g., using `ipaddress`), and deny known local hostnames before fetching content.
