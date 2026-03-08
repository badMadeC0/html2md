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

## 2024-11-09 - Denial of Service (DoS) Risk in HTML Conversion
**Vulnerability:** The `cli.py` script used `requests.get()` to fetch URL content without an explicit input length limit or streaming validation. An attacker could provide a link to a multi-gigabyte file or an infinite stream, exhausting memory and causing a Denial of Service.
**Learning:** Default behavior of `requests.get()` reads the entire response into memory. Unbounded memory allocation based on untrusted input is a significant vulnerability.
**Prevention:** Always use `stream=True` with `requests.get()` when downloading untrusted content. Enforce a maximum file size using the `Content-Length` header (if present) and iterate over response chunks, checking the total accumulated size. Stop and raise an error if it exceeds the limit.
