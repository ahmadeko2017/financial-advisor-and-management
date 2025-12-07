from httpx import Client, ASGITransport

from app.main import app

transport = ASGITransport(app=app)
client = Client(transport=transport, base_url="http://testserver")

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
