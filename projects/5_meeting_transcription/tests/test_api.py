"""Tests for the Meeting Transcription API."""
from fastapi.testclient import TestClient
from src.api.app import app

client = TestClient(app)


class TestMeetingAPIRoutes:
    def test_process_meeting(self):
        resp = client.post(
            "/api/v1/process",
            json={"audio_path": "test.wav"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "segments" in data
        assert "action_items" in data
        assert data["indexed_count"] > 0

    def test_search_empty(self):
        resp = client.post(
            "/api/v1/search",
            json={"query": "roadmap"},
        )
        assert resp.status_code == 200

    def test_stats(self):
        resp = client.get("/api/v1/stats")
        assert resp.status_code == 200
        assert "indexed_documents" in resp.json()

    def test_search_after_process(self):
        # Process first
        client.post("/api/v1/process", json={"audio_path": "test.wav"})
        # Then search
        resp = client.post(
            "/api/v1/search",
            json={"query": "mock transcription"},
        )
        assert resp.status_code == 200
