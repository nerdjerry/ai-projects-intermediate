"""
Mock transcriber for development and testing.

This module provides a lightweight ``ITranscriber`` implementation that
returns hard-coded transcription segments, eliminating the need for a
real ASR model (e.g., Whisper) during local development and unit tests.

Design Principles:
    - Liskov Substitution Principle (LSP): ``MockTranscriber`` fully
      satisfies the ``ITranscriber`` contract, so it can be injected
      anywhere a real transcriber is expected.
    - Dependency Inversion Principle (DIP): Because the ``MeetingService``
      depends on the ``ITranscriber`` abstraction, swapping this mock for
      a production implementation requires only a configuration change.
"""

from ..interfaces.transcriber import ITranscriber, TranscriptionSegment


class MockTranscriber(ITranscriber):
    """Returns static placeholder transcription segments.

    Useful for integration tests and UI prototyping.  Replace with a
    ``WhisperTranscriber`` (or similar) for real audio processing — the
    swap is seamless thanks to LSP.
    """

    async def transcribe(self, audio_path: str) -> list[TranscriptionSegment]:
        """Return two hard-coded segments simulating a brief meeting.

        Args:
            audio_path: Ignored in this mock; accepted for interface
                compatibility.

        Returns:
            A list of two ``TranscriptionSegment`` objects.
        """
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
