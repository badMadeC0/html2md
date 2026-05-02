# CLI Mocking Dependency Extraction Learning

When refactoring entrypoints that dynamically load external dependencies (e.g. `try: import requests`), the original tests may mock the top-level modules (like `@patch('requests.Session.get')`).
If we extract the `import requests` logic into a helper function like `_load_dependencies()`, we must update the tests to `@patch('html2md.cli._load_dependencies')` instead.

This is especially critical when the test environment might not actually have those dependencies installed (`requests`, `markdownify`). If a test `@patch`es a module that is not installed, the test collection process will fail with `ModuleNotFoundError` during setup before the test even executes.
Mocking the internal boundary (`_load_dependencies`) completely isolates the test from environmental constraints.

Furthermore, when testing file system operations and mocking `builtins.open`, caution is needed because libraries (like `argparse` through `gettext`) use `open()` internally.
Using `side_effect` with a passthrough function `return _original_open(filename, ...)` prevents recursive failures and isolated the mock to only the target output file.
