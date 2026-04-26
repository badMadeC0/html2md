import requests
from unittest.mock import patch, MagicMock
import html2md.cli

with patch('requests.Session.get') as mock_get:
    mock_resp = MagicMock()
    mock_resp.text = "<h1>dummy</h1>"
    mock_resp.raise_for_status.return_value = None
    mock_get.return_value = mock_resp

    html2md.cli.main(['--url', 'http://example.com/foo/../..%2Fsecret.txt'])
