"""Extract action items from transcription segments (SRP)."""
from ..interfaces.transcriber import TranscriptionSegment

# Keywords that suggest action items
ACTION_KEYWORDS = [
    "action item", "to do", "todo", "follow up", "follow-up",
    "next step", "assign", "deadline", "will do", "need to",
    "should", "must", "let's", "please",
]


class ActionExtractor:
    """Extracts action items from transcription segments (SRP)."""

    def extract(self, segments: list[TranscriptionSegment]) -> list[dict[str, str]]:
        """Find segments that contain action items."""
        actions: list[dict[str, str]] = []
        for seg in segments:
            text_lower = seg.text.lower()
            for kw in ACTION_KEYWORDS:
                if kw in text_lower:
                    actions.append({
                        "text": seg.text,
                        "speaker": seg.speaker,
                        "timestamp": f"{seg.start_time:.1f}s - {seg.end_time:.1f}s",
                        "keyword": kw,
                    })
                    break  # one match per segment
        return actions
