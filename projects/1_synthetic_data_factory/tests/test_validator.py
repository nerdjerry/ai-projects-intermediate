"""Tests for the DataValidator."""
from src.services.validator import DataValidator


class TestDataValidator:
    def setup_method(self):
        self.validator = DataValidator(min_length=10)

    def test_validate_keeps_valid_records(self):
        records = [
            {
                "question": "What is photosynthesis?",
                "answer": "The process by which plants convert light to energy.",
            },
        ]
        result = self.validator.validate(records)
        assert len(result) == 1

    def test_validate_filters_short_records(self):
        records = [
            {"question": "Hi?", "answer": "No"},
            {
                "question": "What is the speed of light?",
                "answer": "Approximately 3×10⁸ m/s in vacuum.",
            },
        ]
        result = self.validator.validate(records)
        assert len(result) == 1
        assert result[0]["question"] == "What is the speed of light?"

    def test_validate_filters_missing_fields(self):
        records = [
            {"question": "", "answer": "Some long enough answer here"},
            {"answer": "No question field at all in this record"},
        ]
        result = self.validator.validate(records)
        assert len(result) == 0

    def test_deduplicate_removes_exact_dupes(self):
        records = [
            {"question": "What is AI?", "answer": "Artificial Intelligence"},
            {"question": "What is AI?", "answer": "A field of computer science"},
            {"question": "What is ML?", "answer": "Machine Learning"},
        ]
        result = self.validator.deduplicate(records)
        assert len(result) == 2

    def test_deduplicate_preserves_order(self):
        records = [
            {"question": "First question here?", "answer": "First"},
            {"question": "Second question here?", "answer": "Second"},
            {"question": "First question here?", "answer": "Duplicate"},
        ]
        result = self.validator.deduplicate(records)
        assert result[0]["answer"] == "First"
        assert result[1]["answer"] == "Second"
