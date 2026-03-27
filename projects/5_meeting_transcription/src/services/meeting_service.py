"""
Meeting processing orchestrator (pipeline coordinator).

``MeetingService`` wires together the transcription, diarization,
action-extraction, and indexing steps into a single end-to-end pipeline.

Design Principles:
    - Single Responsibility Principle (SRP): This class's sole job is
      *orchestration*.  It delegates all domain work to injected
      collaborators (transcriber, diarizer, indexer, extractor).
    - Dependency Inversion Principle (DIP): Every collaborator is received
      through the constructor as an *abstraction* (``ITranscriber``,
      ``IDiarizer``, ``IIndexer``), so the service never couples to a
      concrete implementation.
    - Composition over Inheritance: ``MeetingService`` composes
      capabilities by holding references to collaborators rather than
      inheriting from them.
    - Pipeline Pattern: ``process_meeting`` executes a well-defined
      sequence of steps, passing the output of one stage as input to the
      next.
"""

from typing import Any

from ..interfaces.transcriber import ITranscriber, TranscriptionSegment
from ..interfaces.diarizer import IDiarizer
from ..interfaces.indexer import IIndexer
from .action_extractor import ActionExtractor


class MeetingService:
    """Coordinates the full meeting-processing pipeline.

    The pipeline consists of four stages:
    1. **Transcribe** — convert audio to timestamped text segments.
    2. **Diarize** — label each segment with a speaker identity.
    3. **Extract actions** — find segments containing action items.
    4. **Index** — store segments for later retrieval / RAG queries.
    """

    def __init__(
        self,
        transcriber: ITranscriber,
        diarizer: IDiarizer,
        indexer: IIndexer,
    ):
        """Initialize with injected collaborators (DIP).

        Args:
            transcriber: Service that converts audio to text segments.
            diarizer: Service that identifies speaker boundaries.
            indexer: Service that stores documents for search/retrieval.
        """
        self._transcriber = transcriber
        self._diarizer = diarizer
        self._indexer = indexer
        # ActionExtractor is a lightweight, stateless helper — created
        # directly rather than injected, following YAGNI.
        self._extractor = ActionExtractor()

    async def process_meeting(self, audio_path: str) -> dict[str, Any]:
        """Run the full pipeline: transcribe → diarize → extract → index.

        Args:
            audio_path: File-system path to the meeting audio file.

        Returns:
            A dictionary containing:
            - ``segments``: List of transcribed segment dicts.
            - ``action_items``: List of identified action-item dicts.
            - ``indexed_count``: Number of documents stored in the index.
        """
        # Stage 1: Transcribe the audio into text segments
        segments = await self._transcriber.transcribe(audio_path)

        # Stage 2: Identify which speaker produced each time range
        speaker_segments = await self._diarizer.diarize(audio_path)

        # Merge speaker labels into the transcription segments
        merged = self._merge_speakers(segments, speaker_segments)

        # Stage 3: Scan merged segments for action-item keywords
        actions = self._extractor.extract(merged)

        # Stage 4: Prepare documents and index them for later retrieval
        docs = [
            {
                "text": seg.text,
                "speaker": seg.speaker,
                "start_time": seg.start_time,
                "end_time": seg.end_time,
            }
            for seg in merged
        ]
        indexed = await self._indexer.index(docs)

        return {
            "segments": [
                {
                    "text": s.text,
                    "speaker": s.speaker,
                    "start_time": s.start_time,
                    "end_time": s.end_time,
                }
                for s in merged
            ],
            "action_items": actions,
            "indexed_count": indexed,
        }

    def _merge_speakers(
        self,
        transcription: list[TranscriptionSegment],
        speakers: list[Any],
    ) -> list[TranscriptionSegment]:
        """Assign speaker labels from diarization to transcription segments.

        Uses a simple containment check: a transcription segment receives
        the speaker label of the diarization segment that fully contains
        its time range.

        Args:
            transcription: Segments produced by the transcriber.
            speakers: Speaker segments produced by the diarizer.

        Returns:
            The same transcription list with updated ``speaker`` fields.
        """
        for seg in transcription:
            for spk in speakers:
                # Check if the transcription segment falls entirely within
                # the speaker's time range (containment match).
                if seg.start_time >= spk.start_time and seg.end_time <= spk.end_time:
                    seg.speaker = spk.speaker
                    break
        return transcription
