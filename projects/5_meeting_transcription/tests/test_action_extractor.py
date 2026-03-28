"""
Tests for ``ActionExtractor`` — keyword-based action-item detection.

These tests verify that the extractor correctly identifies segments
containing action keywords and ignores segments without them.

Testing Strategy:
    - **Single action**: One segment with a keyword, one without — only the
      matching segment should be returned.
    - **No actions**: All benign text — the result list should be empty.
    - **Multiple actions**: Two segments with different keywords — both
      should be captured independently.
"""

from src.interfaces.transcriber import TranscriptionSegment
from src.services.action_extractor import ActionExtractor


class TestActionExtractor:
    """Unit tests for the ActionExtractor keyword scanner."""

    def setup_method(self):
        """Create a fresh extractor for each test (test isolation)."""
        self.extractor = ActionExtractor()

    def test_extract_action_items(self):
        """Segments containing action keywords should be extracted."""
        segments = [
            TranscriptionSegment(text="We need to follow up on the budget.", start_time=0, end_time=5, speaker="Alice"),
            TranscriptionSegment(text="The weather is nice today.", start_time=5, end_time=10, speaker="Bob"),
        ]
        actions = self.extractor.extract(segments)
        # Only Alice's segment contains an action keyword ("follow up")
        assert len(actions) == 1
        assert actions[0]["speaker"] == "Alice"

    def test_no_actions(self):
        """Segments without any action keywords should yield an empty list."""
        segments = [
            TranscriptionSegment(text="Hello everyone.", start_time=0, end_time=2, speaker="Alice"),
        ]
        actions = self.extractor.extract(segments)
        assert len(actions) == 0

    def test_multiple_actions(self):
        """Each segment with a keyword should produce its own action entry."""
        segments = [
            TranscriptionSegment(text="Action item: review the contract.", start_time=0, end_time=5, speaker="A"),
            TranscriptionSegment(text="Please send the report.", start_time=5, end_time=10, speaker="B"),
        ]
        actions = self.extractor.extract(segments)
        # Both segments contain different action keywords
        assert len(actions) == 2
