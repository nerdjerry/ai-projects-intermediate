"""
Tests for the DatasetBuilder.

This module contains unit tests for the ``DatasetBuilder`` class defined
in ``src/services/dataset_builder.py``. The tests validate the three
core responsibilities of the builder:

    1. **Text chunking** — splitting long documents at paragraph boundaries.
    2. **Clause labelling** — classifying text by risk level using keywords.
    3. **Q&A pair generation** — creating fine-tuning examples from clauses.

**Testing best practices demonstrated here:**

• **Arrange / Act / Assert** pattern — each test sets up input,
  calls a method, and asserts on the output.
• **Edge cases** — empty input and single-paragraph input are tested
  alongside the happy path.
• **setup_method** — pytest's per-test setup creates a fresh
  ``DatasetBuilder`` instance so tests are independent.

**SOLID relevance:**
Because ``DatasetBuilder`` follows SRP (only dataset construction),
its tests are focused and fast — no mocking of LLM clients or HTTP
servers is needed.
"""
from src.services.dataset_builder import DatasetBuilder


class TestDatasetBuilder:
    """Unit tests for DatasetBuilder's chunking, labelling, and pair generation."""

    def setup_method(self):
        """Create a fresh DatasetBuilder before each test (test isolation)."""
        self.builder = DatasetBuilder()

    def test_chunk_text_basic(self):
        """Verify that text with multiple paragraphs is split into chunks."""
        text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
        chunks = self.builder.chunk_text(text, max_chars=30)
        # With a 30-char budget, at least two chunks are expected.
        assert len(chunks) >= 2

    def test_chunk_text_single(self):
        """Verify that short text produces exactly one chunk."""
        text = "Short text."
        chunks = self.builder.chunk_text(text, max_chars=1000)
        assert len(chunks) == 1

    def test_chunk_text_empty(self):
        """Verify that empty input returns an empty list (edge case)."""
        chunks = self.builder.chunk_text("", max_chars=1000)
        assert chunks == []

    def test_label_clause_high_risk(self):
        """Verify that a clause containing 'indemnify' is labelled high risk."""
        clause = self.builder.label_clause("Party shall indemnify the other party for losses.")
        assert clause.risk_level == "high"
        assert clause.label == "indemnify"

    def test_label_clause_medium_risk(self):
        """Verify that a clause containing 'warranty' is labelled medium risk."""
        clause = self.builder.label_clause("This warranty covers manufacturing defects.")
        assert clause.risk_level == "medium"
        assert clause.label == "warranty"

    def test_label_clause_low_risk(self):
        """Verify that a clause with no risk keywords defaults to low risk."""
        clause = self.builder.label_clause("The meeting will be held on Tuesday.")
        assert clause.risk_level == "low"
        assert clause.label == "general"

    def test_build_qa_pairs(self):
        """Verify that Q&A pairs are generated correctly from Clause objects."""
        from src.services.dataset_builder import Clause
        clauses = [
            Clause(text="Sample text", label="indemnify", risk_level="high"),
        ]
        pairs = self.builder.build_qa_pairs(clauses)
        assert len(pairs) == 1
        # The generated question should reference the clause label.
        assert "indemnify" in pairs[0]["question"]
        # The risk_level should be preserved in the output.
        assert pairs[0]["risk_level"] == "high"
