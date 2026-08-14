from src.html2md.app import app

def test_headers():
    client = app.test_client()
    response = client.get('/health')
    print(response.headers)

if __name__ == '__main__':
    test_headers()
