# html2md-cli Code Review

## 1. Health Summary
- **Architecture**: Poor modularity; monolithic scripts.
- **Code Quality**: Fair; defensive practices, but excessive nesting and swallowed exceptions.
- **Testing**: Moderate; requires setup, lacks end-to-end integration depth.
- **CI/CD**: Basic; misses linting, SAST, and formatting gates.
- **Security**: At risk; SSRF in URL fetching.
- **Performance**: Suboptimal; batch processing is entirely synchronous.

## 2. Critical Issues (P1-first, numbered)
1. **[Security] SSRF Vulnerability**: No private IP validation in `cli.py:process_url`.
2. **[Architecture] God Function**: `cli.py:main` intertwines I/O and CLI logic.
3. **[Security] Swallowed Exceptions**: `gui-url-convert.ps1` suppresses critical creation errors.
4. **[CI/CD] Missing Gates**: No `ruff`, `mypy`, or `bandit`.

## 3. Architecture & Modularity
`cli.py` and `gui-url-convert.ps1` must be broken up (Ports and Adapters) into dedicated modules for networking, I/O, and business logic.

## 4. Code Quality & Correctness
Remove excessive nesting in `cli.py` and premature optimizations (`loads = json.loads`) in `log_export.py`. Avoid broad `except Exception:` blocks.

## 5. Testing & Reliability
Un-mocked end-to-end integration tests are needed. Current tests aggressively mock `requests.Session.get` and do not verify true execution.

## 6. Type Safety & Static Analysis
Add `mypy --strict` and use strong `TypedDict` instead of `object` / raw dicts.

## 7. Performance & Complexity
Use `ThreadPoolExecutor` for concurrent batch fetching in `cli.py`.

## 8. Security & Robustness
SSRF validation is highly necessary. Error catching must be explicitly targeted.

## 9. CI/CD & Tooling
Introduce standard formatting and security tools to GitHub Actions, and run on macOS/Linux targets.
