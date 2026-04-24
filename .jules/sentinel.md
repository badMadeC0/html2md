# Learning Log

## Code Health refactoring in `cli.py`

- The goal was to extract business logic (`_load_dependencies`, `_setup_session`, and `process_url`) out of the `main()` function in `src/html2md/cli.py` to make the function much cleaner.
- The `requests` and `markdownify` dependencies were originally imported inside `main()` inside a `try-except` block to gracefully handle missing dependencies. To retain this behavior while extracting out the logic, I made `_load_dependencies()` return the modules or `(None, None)` upon failure. Then, `requests_mod` and `md_func` are passed as arguments to `_setup_session` and `process_url`.
- A syntax error `SyntaxError: unterminated string literal` was triggered because `base = base.replace('/', '_').replace('\', '_')` had a single backslash inside the string, which escapes the quote. Changing it to `'\\\\'` inside `sed` or Python's `replace` is required.
- In `tests/test_cli_exceptions.py`, mocking `builtins.open` generically caused an issue with `argparse.ArgumentParser` internally trying to load translations via `gettext`, crashing with `TypeError: a bytes-like object is required, not 'MagicMock'` because the test mocked all file opens. The fix was wrapping `builtins.open` such that only calls for `.md` files return a `MagicMock`, while other calls return the real `builtins.open`.
