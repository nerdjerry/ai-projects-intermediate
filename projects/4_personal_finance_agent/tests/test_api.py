"""Tests for the Personal Finance Agent API.

These tests verify the API endpoints work correctly with the in-memory
service implementations. The TestClient is used as a context manager to
trigger the lifespan events that initialize app.state services.
"""
from fastapi.testclient import TestClient
from src.api.app import app


class TestFinanceAPIRoutes:
    def setup_method(self):
        """Create a fresh TestClient for each test.

        Using TestClient as a context manager ensures the lifespan
        events fire, which initializes app.state with service instances.
        """
        self.client = TestClient(app, raise_server_exceptions=True)
        self.client.__enter__()

    def teardown_method(self):
        """Clean up the TestClient after each test."""
        self.client.__exit__(None, None, None)

    def test_add_transaction(self):
        """Adding a transaction should return it with an ID and date."""
        resp = self.client.post(
            "/api/v1/transactions",
            json={"amount": 42.50, "category": "food", "description": "Lunch"},
        )
        assert resp.status_code == 200
        assert resp.json()["amount"] == 42.50

    def test_list_transactions(self):
        """Listing transactions should return a list."""
        resp = self.client.get("/api/v1/transactions")
        assert resp.status_code == 200
        assert isinstance(resp.json(), list)

    def test_get_summary(self):
        """Summary should include total_spending and by_category."""
        resp = self.client.get("/api/v1/summary")
        assert resp.status_code == 200
        data = resp.json()
        assert "total_spending" in data
        assert "by_category" in data

    def test_chat(self):
        """Chat should return a reply based on transaction data."""
        resp = self.client.post(
            "/api/v1/chat",
            json={"message": "How am I spending?"},
        )
        assert resp.status_code == 200
        assert "reply" in resp.json()

    def test_search_memory(self):
        """Memory search should return results (possibly empty)."""
        resp = self.client.get("/api/v1/memory/search?query=tx")
        assert resp.status_code == 200
