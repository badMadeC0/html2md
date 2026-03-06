with open("tests/test_log_export.py", "r") as f:
    content = f.read()

# I noticed the test failure when I did this earlier:
# AssertionError: assert 'formula' == 'literal'
# - literal
# + formula
# Let me look at the test.
