with open('tests/test_cli_exceptions.py', 'r') as f:
    content = f.read()

# I notice that `TestCliExceptions.test_network_error` asserts that the captured string output from stderr has "Network error: Network unreachable"
# but the CI tells us the captured string is completely empty in test_cli_error and test_cli_exceptions.
# In `cli.py`, `fetch_url` catches exceptions and returns a dictionary, which is then handled by `output_result`.
# Wait, let's look at what we've mocked in the test:
# The CI is failing because `fetch_url` uses the global variable `session` inside `main()` instead of `requests.Session().get()`.
# Wait, `fetch_url` captures `response = session.get(target_url, timeout=30)` but the tests mock `requests.Session.get`.
# In `cli.py`, `session = requests.Session()` happens right before we define `fetch_url`.
# So when `requests.Session.get` is mocked, it SHOULD be mocked properly.

# Let's inspect test_cli_error.py
