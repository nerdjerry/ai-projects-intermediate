"""
Abstract interface for speaker diarization.

Speaker diarization answers the question *"who spoke when?"* by labelling
time regions of an audio file with speaker identities.

Design Principles:
    - Dependency Inversion Principle (DIP): The ``MeetingService``
      orchestrator depends on ``IDiarizer`` rather than on a concrete
      diarization library (e.g., pyannote.audio), enabling easy swaps.
    - Single Responsibility Principle (SRP): This interface is concerned
      only with speaker segmentation; transcription and indexing are
      handled by separate interfaces.
    - Liskov Substitution Principle (LSP): Mock, rule-based, or ML-backed
      diarizers are interchangeable without modifying callers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SpeakerSegment:
    """A contiguous time range attributed to a single speaker.

    Attributes:
        speaker: A label identifying the speaker (e.g., ``"Speaker 1"``).
        start_time: Start of the segment in seconds.
        end_time: End of the segment in seconds.
    """
    speaker: str
    start_time: float
    end_time: float


class IDiarizer(ABC):
    """Contract for services that perform speaker diarization on audio.

    Implementations might use ML models (pyannote), cloud APIs, or return
    static data for testing.  Callers depend only on this abstraction (DIP).
    """

    @abstractmethod
    async def diarize(self, audio_path: str) -> list[SpeakerSegment]:
        """Identify and label speakers across the duration of an audio file.

        Args:
            audio_path: File-system path to the audio file.

        Returns:
            A list of ``SpeakerSegment`` objects, each mapping a time
            range to a speaker label.
        """
        ...
