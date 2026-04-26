import sys
from unittest.mock import MagicMock, patch

def main():
    import json

    def fetch():
        print("json inside fetch:", json)
        try:
            json.loads('invalid')
        except json.JSONDecodeError:
            print("caught")

    fetch()

mock_json = MagicMock()
mock_json.JSONDecodeError = ValueError

with patch.dict(sys.modules, {'json': mock_json}):
    main()
