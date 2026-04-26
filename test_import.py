import sys
from unittest.mock import MagicMock, patch

mock_requests = MagicMock()

def main():
    import requests
    print("requests inside main is mock:", requests is mock_requests)

import requests  # Real requests

with patch.dict(sys.modules, {'requests': mock_requests}):
    main()
