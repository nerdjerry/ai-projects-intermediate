"""
Tests for ``MeetingService`` — the meeting-processing orchestrator.

These tests use mock collaborators (``MockTranscriber``, ``MockDiarizer``,
``InMemoryIndexer``) to verify pipeline orchestration without requiring
real audio files or ML models — demonstrating the power of Dependency
Inversion (DIP).

Testing Strategy:
    - **Process meeting**: Runs the full pipeline and checks that segments,
      action items, and indexed-count are all present in the result.
    - **Indexes segments**: Confirms that transcription segments are
      persisted in the indexer after processing.
"""

import pytest
from src.services.meeting_service import MeetingService
from src.services.mock_transcriber import MockTranscriber
from src.services.mock_diarizer import MockDiarizer
from src.services.in_memory_indexer import InMemoryIndexer


class TestMeetingService:
    """Integration tests for the MeetingService pipeline orchestrator."""

    def setup_method(self):
        """Wire up the service with mock/in-memory collaborators (DIP)."""
        self.indexer = InMemoryIndexer()
        self.service = MeetingService(
            transcriber=MockTranscriber(),
            diarizer=MockDiarizer(),
            indexer=self.indexer,
        )

    @pytest.mark.asyncio
    async def test_process_meeting(self):
        """The pipeline should return segments, actions, and indexed count."""
        result = await self.service.process_meeting("test.wav")
        # At least the mock transcriber's segments should be present
        assert len(result["segments"]) > 0
        # Action items key must exist (may be empty if no keywords match)
        assert "action_items" in result
        # The indexer should have received documents
        assert result["indexed_count"] > 0

    @pytest.mark.asyncio
    async def test_process_indexes_segments(self):
        """After processing, the indexer should contain the transcribed docs."""
        await self.service.process_meeting("test.wav")
        # Verify the indexer's internal count reflects the indexed segments
        assert self.indexer.document_count > 0
