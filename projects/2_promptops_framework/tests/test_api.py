"""Tests for the FastAPI endpoints.

Verifies that the API correctly evaluates prompts, handles invalid inputs,
and returns appropriate error codes.
"""
from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)


class TestAPIRoutes:
    def test_evaluate_endpoint(self):
        """Valid evaluate request should return metric scores."""
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
        """Requesting nonexistent metrics should return 400."""
        resp = client.post(
            "/api/v1/evaluate",
            json={
                "predictions": ["a"],
                "references": ["a"],
                "metrics": ["nonexistent_metric"],
            },
        )
        assert resp.status_code == 400

    def test_evaluate_length_mismatch(self):
        """Mismatched prediction/reference lengths should return 400, not 500."""
        resp = client.post(
            "/api/v1/evaluate",
            json={
                "predictions": ["a", "b"],
                "references": ["a"],
                "metrics": ["exact_match"],
            },
        )
        assert resp.status_code == 400
        assert "same length" in resp.json()["detail"]

    def test_get_prompt_not_found(self):
        """Requesting a nonexistent prompt should return 404."""
        resp = client.get("/api/v1/prompts/nonexistent_prompt_xyz")
        assert resp.status_code == 404
