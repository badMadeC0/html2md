import re

files = [
    'tests/test_cli_exceptions.py',
    'tests/test_cli_security.py'
]

for file in files:
    with open(file, 'r') as f:
        content = f.read()

    # Change patch("requests.sessions.Session.get") to patch("requests.Session")
    content = content.replace('patch("requests.sessions.Session.get")', 'patch("requests.Session")')
    content = content.replace("patch('requests.sessions.Session.get')", "patch('requests.Session')")

    # In test_network_error: mock_get -> mock_session_cls
    # mock_session_cls.return_value.get.side_effect = ...

    with open(file, 'w') as f:
        f.write(content)

with open('tests/test_cli_error.py', 'r') as f:
    content = f.read()

content = content.replace("patch('requests.sessions.Session.get', mock_session.get)", "patch('requests.Session', return_value=mock_session)")

with open('tests/test_cli_error.py', 'w') as f:
    f.write(content)
