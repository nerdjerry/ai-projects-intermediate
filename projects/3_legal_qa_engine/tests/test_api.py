"""Tests for the Legal Q&A Engine API."""
from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)


class TestLegalAPIRoutes:
    def test_chunk_and_label(self):
        resp = client.post(
            "/api/v1/chunk",
            json={"text": "The party shall indemnify all losses.\n\nThis warranty is limited.", "max_chars": 100},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) >= 1

    def test_summarize(self):
        resp = client.post(
            "/api/v1/summarize",
            json={"text": "This is a legal document with several clauses about liability and indemnification."},
        )
        assert resp.status_code == 200
        assert "summary" in resp.json()

    def test_analyze_risk(self):
        resp = client.post(
            "/api/v1/analyze-risk",
            json={"text": "The party shall indemnify the other for any breach of this agreement."},
        )
        assert resp.status_code == 200
        assert "findings" in resp.json()

    def test_ask(self):
        resp = client.post(
            "/api/v1/ask",
            json={"question": "What is the liability?", "context": "Liability is limited to direct damages."},
        )
        assert resp.status_code == 200
        assert "answer" in resp.json()

    def test_summarize_empty_text(self):
        resp = client.post("/api/v1/summarize", json={"text": ""})
        assert resp.status_code == 422  # validation error
