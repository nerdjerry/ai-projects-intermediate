"""Orchestrates transcription, diarization, and indexing (SRP: orchestration)."""
from typing import Any

from ..interfaces.transcriber import ITranscriber, TranscriptionSegment
from ..interfaces.diarizer import IDiarizer
from ..interfaces.indexer import IIndexer
from .action_extractor import ActionExtractor


class MeetingService:
    """Coordinates the meeting processing pipeline."""

    def __init__(
        self,
        transcriber: ITranscriber,
        diarizer: IDiarizer,
        indexer: IIndexer,
    ):
        self._transcriber = transcriber
        self._diarizer = diarizer
        self._indexer = indexer
        self._extractor = ActionExtractor()

    async def process_meeting(self, audio_path: str) -> dict[str, Any]:
        """Full pipeline: transcribe → diarize → extract actions → index."""
        segments = await self._transcriber.transcribe(audio_path)
        speaker_segments = await self._diarizer.diarize(audio_path)

        # Merge speaker info into transcription segments
        merged = self._merge_speakers(segments, speaker_segments)

        # Extract action items
        actions = self._extractor.extract(merged)

        # Index for search
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
        """Assign speaker labels to transcription segments."""
        for seg in transcription:
            for spk in speakers:
                if seg.start_time >= spk.start_time and seg.end_time <= spk.end_time:
                    seg.speaker = spk.speaker
                    break
        return transcription
