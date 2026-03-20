from fastapi.testclient import TestClient

from src.app import app


def test_root_returns_page_title():
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert "Automated Market Scanner" in response.text
