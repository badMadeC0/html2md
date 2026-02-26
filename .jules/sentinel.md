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

## 2024-10-24 - Stored XSS in Markdown Output
**Vulnerability:** The `html2md` tool converted HTML to Markdown without sanitization, preserving dangerous tags like `<script>`, `<style>`, and `<iframe>`. If the generated Markdown is viewed in a viewer that supports raw HTML, this could lead to Stored XSS.
**Learning:** Markdown converters often preserve raw HTML by default to support features not present in Markdown. Always check if the converter has options to strip dangerous tags.
**Prevention:** Configure `markdownify` (or similar tools) with `strip=['script', 'style', 'iframe', 'object', 'embed', 'link', 'meta']` to remove these tags during conversion.
