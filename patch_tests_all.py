import re

files = [
    'tests/test_cli_exceptions.py',
    'tests/test_cli_security.py'
]

for file in files:
    with open(file, 'r') as f:
        content = f.read()

    content = content.replace('patch("requests.Session.get")', 'patch("requests.sessions.Session.get")')
    content = content.replace("patch('requests.Session.get')", "patch('requests.sessions.Session.get')")

    with open(file, 'w') as f:
        f.write(content)

with open('tests/test_cli_error.py', 'r') as f:
    content = f.read()

# For test_cli_error.py, patch sys.modules fails due to Py3.14 import caching.
# Instead of patch.dict on sys.modules, patch requests.sessions.Session.get !
content = content.replace("with patch.dict(sys.modules, {'requests': mock_requests, 'markdownify': mock_markdownify}):",
                          "with patch('requests.sessions.Session.get', mock_session.get), patch('html2md.cli.md', mock_markdownify.markdownify):")

content = content.replace("mock_requests.RequestException = requests.RequestException", "")
content = content.replace("mock_requests.Session.return_value = mock_session", "")
content = content.replace("mock_requests = MagicMock()", "")

with open('tests/test_cli_error.py', 'w') as f:
    f.write(content)
