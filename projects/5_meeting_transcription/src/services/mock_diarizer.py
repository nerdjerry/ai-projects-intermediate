"""Mock diarizer for testing (LSP — swap for pyannote)."""
from ..interfaces.diarizer import IDiarizer, SpeakerSegment


class MockDiarizer(IDiarizer):
    """Returns placeholder speaker segments."""

    async def diarize(self, audio_path: str) -> list[SpeakerSegment]:
        return [
            SpeakerSegment(speaker="Speaker 1", start_time=0.0, end_time=5.0),
            SpeakerSegment(speaker="Speaker 2", start_time=5.0, end_time=10.0),
        ]
