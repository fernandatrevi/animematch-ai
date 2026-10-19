"""API integration tests without external network calls."""
from fastapi.testclient import TestClient
import server

client = TestClient(server.app)


def test_homepage_returns_html():
    response = client.get("/")
    assert response.status_code == 200
    assert "Find your next" in response.text
    assert "powered by machine learning" not in response.text.lower()


def test_catalog_endpoint(monkeypatch):
    monkeypatch.setattr(server, "get_catalog", lambda: (server.sample_catalog(), "Offline demo"))
    response = client.get("/api/catalog")
    assert response.status_code == 200
    assert response.json()["count"] == 18


def test_recommendations_endpoint(monkeypatch):
    monkeypatch.setattr(server, "get_catalog", lambda: (server.sample_catalog(), "Offline demo"))
    response = client.post("/api/recommend", json={"favorites": ["Death Note"], "limit": 5})
    assert response.status_code == 200
    assert len(response.json()["items"]) == 5
    assert all(item["title"] != "Death Note" for item in response.json()["items"])


def test_missing_preferences_is_validation_error(monkeypatch):
    monkeypatch.setattr(server, "get_catalog", lambda: (server.sample_catalog(), "Offline demo"))
    response = client.post("/api/recommend", json={})
    assert response.status_code == 400
