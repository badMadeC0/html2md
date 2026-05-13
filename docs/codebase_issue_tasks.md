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
## 3) Docs/Comment Discrepancy Task: Resolve CLI source-of-truth conflict

**Evidence**
- README describes `html2md` as a placeholder runtime command.
- Other repository guidance (for example `CLAUDE.md` and `.github/copilot-instructions.md`) also describes `src/html2md/cli.py` as a placeholder stub.
- The current CLI includes concrete conversion flow (`--url`, `--batch`, requests fetch, markdownify conversion, file output support).
- As written, a docs-only update could bless behavior that is out of contract with the rest of the repository guidance.

**Locations**
- `README.md`
- `CLAUDE.md`
- `.github/copilot-instructions.md`
- `src/html2md/cli.py`

**Proposed task**
- First decide and document the source of truth for CLI behavior: either `src/html2md/cli.py` must match the placeholder-stub contract, or the repository documentation must be updated to reflect the implemented runtime behavior.
- After that decision, update all affected docs and/or implementation together so the repository presents one consistent contract.
- Explicitly document the chosen contract, including any supported options, constraints, exit-code behavior, and dependency expectations that should remain visible to contributors.

**Acceptance criteria**
- A single source of truth for CLI behavior is identified and recorded in the updated task output.
- If the placeholder-stub contract is retained, `src/html2md/cli.py` and contributor-facing docs consistently describe that placeholder behavior.
- If the current runtime behavior is retained, all relevant docs (not just `README.md`) are updated to match it.
- A docs-focused test/checklist step is added to prevent future drift across contributor guidance and user-facing documentation.

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
