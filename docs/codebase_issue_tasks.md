# Codebase Issue Backlog (2026-04-28)

This document lists four scoped follow-up tasks discovered during a repository scan.

## 1) Typo/UX Task: Fix missing whitespace in dependency error message

**Evidence**
- In the CLI import error path, two adjacent string literals are concatenated without a space after the period.
- Current output can render as: `Error: Missing dependency requests.Please run: ...`.

**Location**
- `src/html2md/cli.py`

**Proposed task**
- Update the error message so the sentence spacing is correct and user-facing output is readable.

**Acceptance criteria**
- Error output includes a space after the period (`... dependency <name>. Please run ...`).
- Existing error-path tests are updated/added to assert exact message formatting.

---

## 2) Bug Task: Return non-zero exit code when conversions fail

**Evidence**
- `process_url()` prints network/conversion/file errors but does not communicate failure back to `main()`.
- `main()` currently returns `0` after processing URL(s) even when all conversions fail.

**Location**
- `src/html2md/cli.py`

**Impact**
- Automation/CI scripts can treat failed runs as successful.

**Proposed task**
- Make `process_url()` return a success/failure boolean.
- Aggregate per-item results in `main()` and return `1` if any requested conversion fails.

**Acceptance criteria**
- Single URL failure exits non-zero.
- Batch mode exits non-zero if at least one URL fails.
- Batch mode exits zero only when all attempted conversions succeed.

---

## 3) Docs/Comment Discrepancy Task: Align README with actual CLI behavior

**Evidence**
- README describes `html2md` as a placeholder runtime command.
- The current CLI includes concrete conversion flow (`--url`, `--batch`, requests fetch, markdownify conversion, file output support).

**Locations**
- `README.md`
- `src/html2md/cli.py`

**Proposed task**
- Rewrite README sections that call the CLI a placeholder so documentation matches implemented behavior and constraints.
- Explicitly document supported schemes, exit-code behavior, and dependency requirements.

**Acceptance criteria**
- README no longer labels the CLI as placeholder-only.
- CLI options and observed behavior match docs.
- A docs-focused test/checklist step is added to prevent future drift.

---

## 4) Test Improvement Task: Strengthen CLI smoke coverage beyond return code

**Evidence**
- Smoke test only asserts `--help` returns zero.
- It does not assert that expected options appear, and it uses `shell=True` unnecessarily.

**Location**
- `tests/test_cli_smoke.py`

**Proposed task**
- Replace shell-based invocation with argument-list invocation (`subprocess.run([...])`).
- Assert help output includes critical flags (`--url`, `--batch`, `--outdir`).

**Acceptance criteria**
- Smoke test validates both successful execution and basic CLI contract.
- Test remains platform-agnostic and avoids shell quoting edge cases.
