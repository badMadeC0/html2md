import requests
from unittest.mock import MagicMock

mock_requests = MagicMock()
mock_requests.RequestException = requests.RequestException

mock_session = MagicMock()
mock_requests.Session.return_value = mock_session

# Here we use the exception class
mock_session.get.side_effect = requests.RequestException("Network error")

def main():
    session = mock_requests.Session()
    try:
        response = session.get("http://example.com")
        print("response:", response)
    except requests.RequestException as e:
        print("Caught:", type(e), e)

main()
