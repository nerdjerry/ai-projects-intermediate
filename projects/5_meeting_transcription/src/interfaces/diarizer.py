"""Speaker diarization interface."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class SpeakerSegment:
    """A time range with speaker identity."""
    speaker: str
    start_time: float
    end_time: float


class IDiarizer(ABC):
    """Abstract speaker diarization service (DIP)."""

    @abstractmethod
    async def diarize(self, audio_path: str) -> list[SpeakerSegment]:
        """Identify speakers in an audio file."""
        ...
