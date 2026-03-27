"""
Abstract interface for audio transcription services.

This module defines both the data model (``TranscriptionSegment``) and the
service contract (``ITranscriber``) for converting audio files into
timestamped text segments.

Design Principles:
    - Dependency Inversion Principle (DIP): Higher-level orchestration
      (``MeetingService``) depends on this abstraction, not on a specific
      ASR (Automatic Speech Recognition) engine such as Whisper.
    - Liskov Substitution Principle (LSP): Any subclass — mock, Whisper,
      cloud-based — can replace ``ITranscriber`` without affecting callers.
    - Single Responsibility Principle (SRP): The interface handles *only*
      transcription; speaker identification is a separate concern
      (``IDiarizer``).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass
class TranscriptionSegment:
    """An individual segment of transcribed audio.

    Attributes:
        text: The transcribed text content.
        start_time: Start timestamp in seconds.
        end_time: End timestamp in seconds.
        speaker: Optional speaker label (may be filled by a diarizer).
    """
    text: str
    start_time: float
    end_time: float
    speaker: str = ""


class ITranscriber(ABC):
    """Contract for services that transcribe audio into text segments.

    Implementations may use local models (e.g., OpenAI Whisper), cloud APIs
    (e.g., Google Speech-to-Text), or simple mocks for testing.  The rest
    of the system depends only on this abstraction (DIP).
    """

    @abstractmethod
    async def transcribe(self, audio_path: str) -> list[TranscriptionSegment]:
        """Transcribe an audio file and return timestamped segments.

        Args:
            audio_path: File-system path to the audio file.

        Returns:
            An ordered list of ``TranscriptionSegment`` objects covering
            the full duration of the audio.
        """
        ...
