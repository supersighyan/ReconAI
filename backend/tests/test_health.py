from fastapi.testclient import TestClient


def test_application_starts(client: TestClient) -> None:
    assert client.app.title == "ReconAI"


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
