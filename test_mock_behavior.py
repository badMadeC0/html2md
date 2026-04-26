import sys
import unittest
from unittest.mock import patch, MagicMock

# Simulate exactly what happens in test_cli_error.py
mock_requests = MagicMock()
import requests
mock_requests.RequestException = requests.RequestException

mock_session = MagicMock()
mock_requests.Session.return_value = mock_session
mock_session.get.side_effect = requests.RequestException("Network error")

def main():
    import requests
    session = requests.Session()

    def fetch_url():
        try:
            response = session.get("http://example.com")
            print("response text:", response.text)
        except requests.RequestException as e:
            print("Caught RequestException:", e)
        except Exception as e:
            print("Caught Exception:", e)

    fetch_url()

with patch.dict(sys.modules, {'requests': mock_requests}):
    main()
