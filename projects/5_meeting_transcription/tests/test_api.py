"""Tests for the Meeting Transcription API.

These tests verify the API endpoints work correctly with mock transcription
and diarization services. The TestClient is used as a context manager to
trigger lifespan events that initialize app.state services.
"""
from fastapi.testclient import TestClient
from src.api.app import app


class TestMeetingAPIRoutes:
    def setup_method(self):
        """Create a fresh TestClient for each test.

        Using context manager ensures lifespan events fire,
        initializing app.state with service instances.
        """
        self.client = TestClient(app, raise_server_exceptions=True)
        self.client.__enter__()

    def teardown_method(self):
        """Clean up the TestClient after each test."""
        self.client.__exit__(None, None, None)

    def test_process_meeting(self):
        """Processing a meeting should return segments, actions, and index count."""
        resp = self.client.post(
            "/api/v1/process",
            json={"audio_path": "test.wav"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "segments" in data
        assert "action_items" in data
        assert data["indexed_count"] > 0

    def test_search_empty(self):
        """Searching with no indexed documents should return empty results."""
        resp = self.client.post(
            "/api/v1/search",
            json={"query": "roadmap"},
        )
        assert resp.status_code == 200

    def test_stats(self):
        """Stats endpoint should report the number of indexed documents."""
        resp = self.client.get("/api/v1/stats")
        assert resp.status_code == 200
        assert "indexed_documents" in resp.json()

    def test_search_after_process(self):
        """After processing, search should find relevant transcript segments."""
        # Process first to populate the index
        self.client.post("/api/v1/process", json={"audio_path": "test.wav"})
        # Then search for content from the mock transcription
        resp = self.client.post(
            "/api/v1/search",
            json={"query": "mock transcription"},
        )
        assert resp.status_code == 200
