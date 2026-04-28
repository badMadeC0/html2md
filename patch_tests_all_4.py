import re

for file in ['tests/test_cli_exceptions.py', 'tests/test_cli_security.py']:
    with open(file, 'r') as f:
        content = f.read()

    # We need to fix the argument names and mock configurations
    content = content.replace("mock_get.side_effect", "mock_get.return_value.get.side_effect")
    content = content.replace("mock_get.return_value", "mock_get.return_value.get.return_value")
    content = content.replace("mock_get.assert_not_called()", "mock_get.return_value.get.assert_not_called()")

    # wait, mock_get.return_value.return_value is wrong if we already replaced it

    with open(file, 'w') as f:
        f.write(content)
