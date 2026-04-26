import sys
import unittest
from unittest.mock import patch, MagicMock
import requests

def main():
    import requests
    session = requests.Session()

    def fetch_url():
        try:
            response = session.get("http://example.com/foo/../..%2Fsecret.txt")
            print("response text:", response.text)
        except requests.RequestException as e:
            print("Caught RequestException:", e)
        except Exception as e:
            print("Caught Exception:", e)

    fetch_url()

@patch("requests.Session.get")
def test_it(mock_get):
    response = MagicMock()
    response.text = "<h1>dummy</h1>"
    response.raise_for_status.return_value = None
    mock_get.return_value = response
    main()

test_it()
