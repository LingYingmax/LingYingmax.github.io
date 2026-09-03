from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_application_can_be_created() -> None:
    assert app.title == "LingYingmax Blog API"


def test_health_check_returns_ok() -> None:
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
