import requests
from unittest.mock import patch
from html2md.cli import main

with patch("requests.Session.get") as mock_get:
    mock_get.side_effect = requests.RequestException("Network unreachable")
    main(["--url", "http://example.com"])
