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

## 2024-10-24 - SSRF and Local File Inclusion via CLI
**Vulnerability:** The `html2md` CLI accepted any URL scheme and passed it directly to the `requests` library without validation. This allowed an attacker to input arbitrary URL schemes (like `file://`) to potentially read local files or perform Server-Side Request Forgery (SSRF) attacks against internal services (like `http://localhost`).
**Learning:** Security validation must be enforced at the lowest possible layer (the CLI engine), not just in the UI wrappers (the GUI script had some validation, but the core CLI engine did not). Relying on the underlying library (`requests`) to handle all validation securely is insufficient.
**Prevention:** Always validate and enforce an allowlist for URL schemes (`http://`, `https://`) in the core engine before making outbound requests.
