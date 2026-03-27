"""
Mock speaker diarizer for development and testing.

This module provides a lightweight ``IDiarizer`` implementation that
returns hard-coded speaker segments, allowing the full meeting-processing
pipeline to run without a real diarization model (e.g., pyannote.audio).

Design Principles:
    - Liskov Substitution Principle (LSP): ``MockDiarizer`` honours the
      ``IDiarizer`` contract, so it can be substituted for any production
      diarizer without affecting callers.
    - Dependency Inversion Principle (DIP): The ``MeetingService`` depends
      on ``IDiarizer``, not on this concrete class, making the swap
      transparent.
"""

from ..interfaces.diarizer import IDiarizer, SpeakerSegment


class MockDiarizer(IDiarizer):
    """Returns static placeholder speaker segments.

    The segments align with those produced by ``MockTranscriber`` so the
    ``MeetingService._merge_speakers`` step works correctly during tests.
    """

    async def diarize(self, audio_path: str) -> list[SpeakerSegment]:
        """Return two hard-coded speaker segments covering 0–10 s.

        Args:
            audio_path: Ignored in this mock; accepted for interface
                compatibility.

        Returns:
            A list of two ``SpeakerSegment`` objects.
        """
        return [
            SpeakerSegment(speaker="Speaker 1", start_time=0.0, end_time=5.0),
            SpeakerSegment(speaker="Speaker 2", start_time=5.0, end_time=10.0),
        ]
