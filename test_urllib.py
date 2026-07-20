import urllib.request
import urllib.error

url = "https://api.github.com/repos/badMadeC0/html2md/issues/1224/comments"
req = urllib.request.Request(url)
try:
    with urllib.request.urlopen(req) as resp:
        print("Success")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(e.read())
