with open('tests/test_cli_error.py', 'r') as f:
    content = f.read()

content = content.replace("patch('html2md.cli.md', mock_markdownify.markdownify)", "patch('markdownify.markdownify', mock_markdownify.markdownify)")

with open('tests/test_cli_error.py', 'w') as f:
    f.write(content)
