with open('tests/test_cli_error.py', 'r') as f:
    content = f.read()

# I see what happens in test_cli_error.py:
# `output = captured_stderr.getvalue()`
# The error `Network error` was expected to be on `stderr`.
# But in `cli.py`, `output_result` does:
# `if result["error"]:`
# `    print(result["error"], file=sys.stderr)`
# Wait, why was `stderr` empty? Let's run my `debug_mock.py` equivalent of `test_cli_error.py`.
