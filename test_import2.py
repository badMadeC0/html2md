import sys
import requests
from unittest.mock import MagicMock, patch

mock_requests = MagicMock()
mock_requests.RequestException = requests.RequestException

def main():
    import requests
    print("requests is mock:", requests is mock_requests)
    try:
        raise requests.RequestException("test")
    except requests.RequestException:
        print("Caught correctly!")
    except Exception:
        print("Caught incorrectly!")

with patch.dict(sys.modules, {'requests': mock_requests}):
    main()
