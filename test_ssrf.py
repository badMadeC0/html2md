import requests

session = requests.Session()
response = session.get("http://localhost:10000/health", timeout=3)
print(response.text)
