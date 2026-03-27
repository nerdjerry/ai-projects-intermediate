"""Tests for the MeetingService."""
import pytest
from src.services.meeting_service import MeetingService
from src.services.mock_transcriber import MockTranscriber
from src.services.mock_diarizer import MockDiarizer
from src.services.in_memory_indexer import InMemoryIndexer


class TestMeetingService:
    def setup_method(self):
        self.indexer = InMemoryIndexer()
        self.service = MeetingService(
            transcriber=MockTranscriber(),
            diarizer=MockDiarizer(),
            indexer=self.indexer,
        )

    @pytest.mark.asyncio
    async def test_process_meeting(self):
        result = await self.service.process_meeting("test.wav")
        assert len(result["segments"]) > 0
        assert "action_items" in result
        assert result["indexed_count"] > 0

    @pytest.mark.asyncio
    async def test_process_indexes_segments(self):
        await self.service.process_meeting("test.wav")
        assert self.indexer.document_count > 0
