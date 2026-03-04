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

## 2024-03-04 - Path Traversal Vulnerability in CLI Filename Generation
**Vulnerability:** URL-encoded directory traversal sequences (e.g. `%2f..%2f`) in the target URL were not being correctly stripped by `os.path.basename(url.split('?')[0].rstrip('/'))` when creating the output markdown filename in `src/html2md/cli.py`.
**Learning:** `os.path.basename` is not sufficient to prevent path traversal when dealing with URLs, as URL-encoded separators like `%2f` or `%5c` will not be recognized by `os.path.basename` until they are decoded. A malicious URL could result in files being written outside the intended output directory.
**Prevention:** Always use a dedicated secure filename function (like Werkzeug's `secure_filename` or a custom implementation) that decodes URL parameters first, then explicitly replaces or removes path separators (`/`, `\`), null bytes, and traversal elements (`..`), and strips dangerous leading/trailing characters.
