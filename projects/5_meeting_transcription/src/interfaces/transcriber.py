"""Transcriber interface — swap ASR models (LSP)."""
from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TranscriptionSegment:
    """A segment of transcribed audio."""
    text: str
    start_time: float
    end_time: float
    speaker: str = ""


class ITranscriber(ABC):
    """Abstract transcription service (DIP)."""

    @abstractmethod
    async def transcribe(self, audio_path: str) -> list[TranscriptionSegment]:
        """Transcribe an audio file into segments."""
        ...
