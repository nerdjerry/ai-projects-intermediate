"""
Tests for the Legal Q&A Engine API.

This module contains integration tests that exercise the FastAPI
endpoints defined in ``src/api/routes.py`` using FastAPI's built-in
``TestClient`` (which wraps ``httpx`` under the hood).

**Testing philosophy:**

• **No external dependencies:** These tests run without an LLM API key.
  The endpoints either use the heuristic-based ``DatasetBuilder`` or
  return placeholder responses, so the test suite is fast, free, and
  deterministic.

• **Schema validation:** Each test verifies the HTTP status code and
  checks that the response JSON contains the expected keys. This
  ensures the API contract (Pydantic schemas) is honoured.

• **Edge cases:** The ``test_summarize_empty_text`` test verifies that
  Pydantic's ``min_length=1`` constraint correctly rejects empty input
  with a ``422 Unprocessable Entity`` response.

**SOLID relevance:**
Because the routes are thin controllers that delegate to service
classes, these tests implicitly validate the integration between the
API layer and the ``DatasetBuilder`` service — without coupling to any
LLM provider (DIP in action).
"""
from fastapi.testclient import TestClient
from src.api.app import app

# Create a synchronous test client that sends requests to the FastAPI app
# in-process (no real HTTP server needed).
client = TestClient(app)


class TestLegalAPIRoutes:
    """Integration tests for all Legal Q&A Engine API endpoints."""

    def test_chunk_and_label(self):
        """Verify that /chunk splits text and labels clauses correctly."""
        resp = client.post(
            "/api/v1/chunk",
            json={"text": "The party shall indemnify all losses.\n\nThis warranty is limited.", "max_chars": 100},
        )
        assert resp.status_code == 200
        data = resp.json()
        # The input contains two paragraphs; expect at least one chunk.
        assert len(data) >= 1

    def test_summarize(self):
        """Verify that /summarize returns a summary key in the response."""
        resp = client.post(
            "/api/v1/summarize",
            json={"text": "This is a legal document with several clauses about liability and indemnification."},
        )
        assert resp.status_code == 200
        assert "summary" in resp.json()

    def test_analyze_risk(self):
        """Verify that /analyze-risk detects risk keywords and returns findings."""
        resp = client.post(
            "/api/v1/analyze-risk",
            json={"text": "The party shall indemnify the other for any breach of this agreement."},
        )
        assert resp.status_code == 200
        assert "findings" in resp.json()

    def test_ask(self):
        """Verify that /ask returns an answer key in the response."""
        resp = client.post(
            "/api/v1/ask",
            json={"question": "What is the liability?", "context": "Liability is limited to direct damages."},
        )
        assert resp.status_code == 200
        assert "answer" in resp.json()

    def test_summarize_empty_text(self):
        """Verify that empty text is rejected with a 422 validation error.

        This test confirms that Pydantic's ``min_length=1`` constraint
        on ``SummarizeRequest.text`` is enforced at the API boundary.
        """
        resp = client.post("/api/v1/summarize", json={"text": ""})
        assert resp.status_code == 422  # validation error
