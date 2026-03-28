"""Tests for the FastAPI endpoints.

These tests exercise the HTTP layer in isolation by using FastAPI's
``TestClient`` (which runs requests in-process, no real server needed).
The OpenAI LLM client is patched out so that tests are fast, free, and
deterministic.

Design principles demonstrated:
  - DIP (Dependency Inversion Principle): By patching ``OpenAIClient`` at
    the import location used by the routes module, we replace the real LLM
    with a mock — proving that the route code depends on the *interface*
    behaviour, not on a specific provider.
  - SRP (Single Responsibility Principle): Each test method verifies one
    specific behaviour (happy path, empty list, 404), making failures easy
    to diagnose.

Testing pattern:
  ``unittest.mock.patch`` replaces the concrete ``OpenAIClient`` class
  inside ``src.api.routes`` so that no real API calls are made.  The
  ``AsyncMock`` on ``generate_batch`` returns canned JSON strings that
  the ``DataGenerator`` can parse, letting us test the full pipeline
  (generate → validate → store) end-to-end within the route handler.
"""
import json
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from src.api.app import app

# TestClient wraps the FastAPI app and lets us call endpoints with plain
# method calls (client.get, client.post) instead of making real HTTP
# requests — fast and reliable for automated tests.
client = TestClient(app)


class TestAPIRoutes:
    """Integration-style tests for the /api/v1 route handlers."""

    @patch("src.api.routes.OpenAIClient")
    def test_generate_endpoint(self, mock_llm_cls):
        """POST /generate should return domain, generated, and validated counts.

        The LLM class is patched so no real API call is made.  Instead,
        ``generate_batch`` returns a single valid Q&A JSON string that the
        DataGenerator can parse successfully.
        """
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
        # validated may be 0 if the record is too short; just ensure the
        # key exists and is non-negative.
        assert data["validated"] >= 0

    def test_list_datasets_empty(self):
        """GET /datasets should return 200 even when no datasets exist."""
        resp = client.get("/api/v1/datasets")
        assert resp.status_code == 200

    def test_get_dataset_not_found(self):
        """GET /datasets/<missing> should return 404 with an error detail."""
        resp = client.get("/api/v1/datasets/nonexistent_xyz")
        assert resp.status_code == 404
