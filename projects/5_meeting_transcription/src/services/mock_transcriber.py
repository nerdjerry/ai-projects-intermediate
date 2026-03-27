"""Mock transcriber for testing (LSP — swap for Whisper)."""
from ..interfaces.transcriber import ITranscriber, TranscriptionSegment


class MockTranscriber(ITranscriber):
    """Returns placeholder transcriptions (swap for WhisperTranscriber via LSP)."""

    async def transcribe(self, audio_path: str) -> list[TranscriptionSegment]:
        return [
            TranscriptionSegment(
                text="This is a mock transcription of the meeting.",
                start_time=0.0,
                end_time=5.0,
                speaker="Speaker 1",
            ),
            TranscriptionSegment(
                text="We discussed the project roadmap.",
                start_time=5.0,
                end_time=10.0,
                speaker="Speaker 2",
            ),
        ]
