"""Tests for the DataValidator.

These tests verify the two core responsibilities of ``DataValidator``:
length-based validation and exact-duplicate removal.  Each test method
isolates a single behaviour so that a failure immediately pinpoints the
broken rule.

Design principles demonstrated:
  - LSP (Liskov Substitution Principle): ``DataValidator`` is tested
    through its public API (``validate``, ``deduplicate``), which matches
    the ``IValidator`` interface.  Any alternative validator that satisfies
    the same interface could be tested with a similar suite.
  - SRP (Single Responsibility Principle): Validation and deduplication
    are tested independently, reflecting the fact that they are logically
    separate operations even though they live in the same class.

Testing pattern:
  ``setup_method`` creates a fresh ``DataValidator`` before every test so
  that tests are fully isolated and order-independent.  Each test feeds
  hand-crafted records to the validator and asserts on the returned list,
  covering both "keep" and "reject" paths.
"""
from src.services.validator import DataValidator


class TestDataValidator:
    """Unit tests for the DataValidator service."""

    def setup_method(self):
        """Create a fresh validator with a 10-character minimum for each test."""
        self.validator = DataValidator(min_length=10)

    # --- validate() tests ---------------------------------------------------

    def test_validate_keeps_valid_records(self):
        """Records with sufficiently long question and answer should pass."""
        records = [
            {
                "question": "What is photosynthesis?",
                "answer": "The process by which plants convert light to energy.",
            },
        ]
        result = self.validator.validate(records)
        assert len(result) == 1

    def test_validate_filters_short_records(self):
        """Records whose question or answer is too short should be removed."""
        records = [
            {"question": "Hi?", "answer": "No"},  # both fields too short
            {
                "question": "What is the speed of light?",
                "answer": "Approximately 3×10⁸ m/s in vacuum.",
            },
        ]
        result = self.validator.validate(records)
        assert len(result) == 1
        assert result[0]["question"] == "What is the speed of light?"

    def test_validate_filters_missing_fields(self):
        """Records with empty or absent question/answer fields should fail."""
        records = [
            {"question": "", "answer": "Some long enough answer here"},
            {"answer": "No question field at all in this record"},
        ]
        result = self.validator.validate(records)
        assert len(result) == 0

    # --- deduplicate() tests ------------------------------------------------

    def test_deduplicate_removes_exact_dupes(self):
        """Exact-duplicate questions should be collapsed to one record."""
        records = [
            {"question": "What is AI?", "answer": "Artificial Intelligence"},
            {"question": "What is AI?", "answer": "A field of computer science"},
            {"question": "What is ML?", "answer": "Machine Learning"},
        ]
        result = self.validator.deduplicate(records)
        assert len(result) == 2

    def test_deduplicate_preserves_order(self):
        """The first occurrence of a duplicate should be the one kept."""
        records = [
            {"question": "First question here?", "answer": "First"},
            {"question": "Second question here?", "answer": "Second"},
            {"question": "First question here?", "answer": "Duplicate"},
        ]
        result = self.validator.deduplicate(records)
        assert result[0]["answer"] == "First"
        assert result[1]["answer"] == "Second"
