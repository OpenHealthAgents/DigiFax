from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)

def test_health_check() -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy", "service": "medingest-api"}

def test_live_check() -> None:
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == "OK"
