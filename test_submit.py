import urllib.request
try:
    urllib.request.urlopen('http://localhost:8000')
    print("Agent listener found")
except Exception as e:
    print(f"Error: {e}")
