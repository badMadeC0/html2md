import sys
from unittest.mock import MagicMock, patch

class DummyException(Exception): pass

mock_requests = MagicMock()
mock_requests.RequestException = DummyException

mock_session = MagicMock()
mock_requests.Session.return_value = mock_session
mock_session.get.side_effect = DummyException("Network error")

def main():
    import requests
    session = requests.Session()

    def fetch():
        try:
            print("calling session.get")
            response = session.get("http://example.com")
            print("response:", response)
        except requests.RequestException as e:
            print("caught exception:", e)

    fetch()

with patch.dict(sys.modules, {'requests': mock_requests}):
    main()
