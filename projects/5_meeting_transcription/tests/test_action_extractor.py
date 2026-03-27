"""Tests for the ActionExtractor."""
from src.interfaces.transcriber import TranscriptionSegment
from src.services.action_extractor import ActionExtractor


class TestActionExtractor:
    def setup_method(self):
        self.extractor = ActionExtractor()

    def test_extract_action_items(self):
        segments = [
            TranscriptionSegment(text="We need to follow up on the budget.", start_time=0, end_time=5, speaker="Alice"),
            TranscriptionSegment(text="The weather is nice today.", start_time=5, end_time=10, speaker="Bob"),
        ]
        actions = self.extractor.extract(segments)
        assert len(actions) == 1
        assert actions[0]["speaker"] == "Alice"

    def test_no_actions(self):
        segments = [
            TranscriptionSegment(text="Hello everyone.", start_time=0, end_time=2, speaker="Alice"),
        ]
        actions = self.extractor.extract(segments)
        assert len(actions) == 0

    def test_multiple_actions(self):
        segments = [
            TranscriptionSegment(text="Action item: review the contract.", start_time=0, end_time=5, speaker="A"),
            TranscriptionSegment(text="Please send the report.", start_time=5, end_time=10, speaker="B"),
        ]
        actions = self.extractor.extract(segments)
        assert len(actions) == 2
