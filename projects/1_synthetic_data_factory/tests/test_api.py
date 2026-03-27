"""Tests for the FastAPI endpoints."""
import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.api.app import app

client = TestClient(app)


class TestAPIRoutes:
    @patch("src.api.routes.OpenAIClient")
    def test_generate_endpoint(self, mock_llm_cls):
        mock_instance = mock_llm_cls.return_value
        mock_instance.generate_batch = AsyncMock(
            return_value=[
                json.dumps(
                    {
                        "question": "What is gravity?",
                        "answer": "A fundamental force of nature.",
                    }
                ),
            ]
        )
        resp = client.post(
            "/api/v1/generate",
            json={"domain": "science", "num_samples": 1},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["domain"] == "science"
        assert data["validated"] >= 0

    def test_list_datasets_empty(self):
        resp = client.get("/api/v1/datasets")
        assert resp.status_code == 200

    def test_get_dataset_not_found(self):
        resp = client.get("/api/v1/datasets/nonexistent_xyz")
        assert resp.status_code == 404
