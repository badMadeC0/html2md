# Maintenance Task Proposals

## 1. Typo fix: missing space in dependency error

- **File/line:** `src/html2md/cli.py`, dependency import error message.
- **Issue:** Adjacent string literals produce `requests.Please` instead of `requests. Please` when a dependency is missing.
- **Impact:** User-facing CLI error text looks unpolished and can be harder to read.
- **Task:** Add a leading space before `Please run: ...` and cover the missing-dependency path with a small assertion.

## 2. Bug fix: CLI errors are reported with success exit codes

- **File/line:** `src/html2md/cli.py`, `process_url()` error branches and final URL/batch return path.
- **Issue:** URL processing errors are printed inside `process_url()`, but the helper does not return a status code; `main()` returns `0` after processing even when a URL fails due to network, file, conversion, or unsupported-scheme errors.
- **Impact:** Scripts and CI jobs can treat failed conversions as successful.
- **Task:** Make `process_url()` return `0` or `1`, aggregate URL and batch results, and return non-zero when any requested conversion fails.

## 3. Documentation discrepancy fix: README still describes a placeholder CLI

- **File/line:** `README.md`, repository snapshot and feature bullets.
- **Issue:** The README says the `html2md` CLI is a placeholder that only exposes help behavior and prints a runtime availability message, but the current `cli.py` performs URL fetching, Markdown conversion, batch processing, and optional output-file writing.
- **Impact:** Users and maintainers get conflicting expectations about supported CLI behavior.
- **Task:** Update the README to describe the current source-tree CLI capabilities and explicitly mark any packaging-only features that remain unavailable here.

## 4. Test improvement: assert failure return codes, not just stderr text

- **File/line:** CLI error-path tests under `tests/`.
- **Issue:** Existing CLI error tests verify messages are printed and exceptions are not raised, but they do not assert `main()` return values.
- **Impact:** The current suite can miss regressions where the CLI reports an error but exits successfully.
- **Task:** Add tests for unsupported schemes, network failures, file write failures, and conversion failures that assert both stderr content and non-zero return codes.
