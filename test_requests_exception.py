import sys
import requests
from unittest.mock import patch
from html2md.cli import main

def test_it():
    with patch("requests.Session.get") as mock_get:
        mock_get.side_effect = requests.RequestException("Network unreachable")
        try:
            main(["--url", "http://example.com"])
        except Exception as e:
            print("Main raised:", type(e), e)

test_it()
