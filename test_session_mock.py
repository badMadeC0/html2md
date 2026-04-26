import requests
from unittest.mock import patch

def main():
    import requests
    session = requests.Session()
    try:
        session.get("http://example.com")
        print("Real network!")
    except Exception as e:
        print("Caught:", type(e), e)

with patch("requests.Session.get", side_effect=Exception("Fake error")):
    main()
