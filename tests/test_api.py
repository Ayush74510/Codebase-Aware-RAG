from fastapi.testclient import TestClient
from src.api.main import app


client = TestClient(app)


def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ask_rejects_empty_query():
    response = client.post(
        "/ask",
        json={"query": "", "top_k": 5},
    )

    assert response.status_code == 422


def test_ask_rejects_invalid_top_k():
    response = client.post(
        "/ask",
        json={"query": "test", "top_k": 0},
    )

    assert response.status_code == 422