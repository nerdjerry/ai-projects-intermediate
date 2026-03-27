"""
Keyword-based action-item extractor for meeting transcripts.

This module scans transcription segments for phrases that indicate
actionable follow-ups (e.g., "action item", "please", "need to").

Design Principles:
    - Single Responsibility Principle (SRP): ``ActionExtractor`` does
      exactly one thing — identify action items.  It does not transcribe,
      diarize, or store results; those responsibilities belong to other
      services.
    - Open/Closed Principle (OCP): New action keywords can be added to
      ``ACTION_KEYWORDS`` without modifying the extraction logic itself.
    - Composition over inheritance: ``ActionExtractor`` is a plain class
      (no ABC superclass) because there is currently only one extraction
      strategy.  If a second strategy is needed (e.g., LLM-based), an
      interface can be introduced at that point (YAGNI).
"""

from ..interfaces.transcriber import TranscriptionSegment

# Curated list of phrases that typically signal an action item in meetings.
# Extending this list is the simplest way to improve recall (OCP).
ACTION_KEYWORDS = [
    "action item", "to do", "todo", "follow up", "follow-up",
    "next step", "assign", "deadline", "will do", "need to",
    "should", "must", "let's", "please",
]


class ActionExtractor:
    """Extracts action items from transcription segments using keyword matching.

    Each segment is checked against ``ACTION_KEYWORDS``.  The *first*
    matching keyword wins (one action per segment) to avoid duplicates.
    """

    def extract(self, segments: list[TranscriptionSegment]) -> list[dict[str, str]]:
        """Scan segments and return those containing action-item keywords.

        Args:
            segments: Ordered list of transcription segments to scan.

        Returns:
            A list of dictionaries, each containing:
            - ``text``: The full segment text.
            - ``speaker``: Who said it.
            - ``timestamp``: Formatted start–end time range.
            - ``keyword``: The keyword that triggered the match.
        """
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
                    break  # one match per segment to avoid duplicate entries
        return actions
