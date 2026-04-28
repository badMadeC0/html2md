import re

for file in ['tests/test_cli_exceptions.py', 'tests/test_cli_security.py']:
    with open(file, 'r') as f:
        content = f.read()

    content = content.replace('patch("requests.sessions.Session.get")', 'patch("requests.Session")')
    content = content.replace("patch('requests.sessions.Session.get')", "patch('requests.Session')")

    content = content.replace("mock_get.side_effect =", "mock_get.return_value.get.side_effect =")
    content = content.replace("mock_get.return_value = mock_resp", "mock_get.return_value.get.return_value = mock_resp")
    content = content.replace("mock_get.return_value = response", "mock_get.return_value.get.return_value = response")
    content = content.replace("mock_get.assert_not_called()", "mock_get.return_value.get.assert_not_called()")

    with open(file, 'w') as f:
        f.write(content)

with open('tests/test_cli_exceptions.py', 'r') as f:
    content = f.read()
content = content.replace("mock_get.return_value.get.return_value.get.side_effect = requests.RequestException", "mock_get.return_value.get.side_effect = requests.RequestException")
with open('tests/test_cli_exceptions.py', 'w') as f:
    f.write(content)
