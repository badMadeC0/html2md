import urllib.parse
print(urllib.parse.urlparse("http://169.254.169.254/latest/meta-data/").hostname)
