"""Tests for the FastAPI endpoints."""
from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)


class TestAPIRoutes:
    def test_evaluate_endpoint(self):
        resp = client.post(
            "/api/v1/evaluate",
            json={
                "predictions": ["hello", "world"],
                "references": ["hello", "earth"],
                "metrics": ["exact_match"],
            },
        )
        assert resp.status_code == 200
        assert "scores" in resp.json()
        assert resp.json()["scores"]["exact_match"] == 0.5

    def test_evaluate_invalid_metrics(self):
        resp = client.post(
            "/api/v1/evaluate",
            json={
                "predictions": ["a"],
                "references": ["a"],
                "metrics": ["nonexistent_metric"],
            },
        )
        assert resp.status_code == 400

    def test_get_prompt_not_found(self):
        resp = client.get("/api/v1/prompts/nonexistent_prompt_xyz")
        assert resp.status_code == 404
