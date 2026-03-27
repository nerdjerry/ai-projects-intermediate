"""Tests for the Personal Finance Agent API."""
from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)


class TestFinanceAPIRoutes:
    def test_add_transaction(self):
        resp = client.post(
            "/api/v1/transactions",
            json={"amount": 42.50, "category": "food", "description": "Lunch"},
        )
        assert resp.status_code == 200
        assert resp.json()["amount"] == 42.50

    def test_list_transactions(self):
        resp = client.get("/api/v1/transactions")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_summary(self):
        resp = client.get("/api/v1/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_spending" in data
        assert "by_category" in data

    def test_chat(self):
        resp = client.post(
            "/api/v1/chat",
            json={"message": "How am I spending?"},
        )
        assert resp.status_code == 200
        assert "reply" in resp.json()

    def test_search_memory(self):
        resp = client.get("/api/v1/memory/search?query=tx")
        assert resp.status_code == 200
