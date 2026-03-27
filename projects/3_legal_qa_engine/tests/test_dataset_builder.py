"""Tests for the DatasetBuilder."""
from src.services.dataset_builder import DatasetBuilder


class TestDatasetBuilder:
    def setup_method(self):
        self.builder = DatasetBuilder()

    def test_chunk_text_basic(self):
        text = "Paragraph one.\n\nParagraph two.\n\nParagraph three."
        chunks = self.builder.chunk_text(text, max_chars=30)
        assert len(chunks) >= 2

    def test_chunk_text_single(self):
        text = "Short text."
        chunks = self.builder.chunk_text(text, max_chars=1000)
        assert len(chunks) == 1

    def test_chunk_text_empty(self):
        chunks = self.builder.chunk_text("", max_chars=1000)
        assert chunks == []

    def test_label_clause_high_risk(self):
        clause = self.builder.label_clause("Party shall indemnify the other party for losses.")
        assert clause.risk_level == "high"
        assert clause.label == "indemnify"

    def test_label_clause_medium_risk(self):
        clause = self.builder.label_clause("This warranty covers manufacturing defects.")
        assert clause.risk_level == "medium"
        assert clause.label == "warranty"

    def test_label_clause_low_risk(self):
        clause = self.builder.label_clause("The meeting will be held on Tuesday.")
        assert clause.risk_level == "low"
        assert clause.label == "general"

    def test_build_qa_pairs(self):
        from src.services.dataset_builder import Clause
        clauses = [
            Clause(text="Sample text", label="indemnify", risk_level="high"),
        ]
        pairs = self.builder.build_qa_pairs(clauses)
        assert len(pairs) == 1
        assert "indemnify" in pairs[0]["question"]
        assert pairs[0]["risk_level"] == "high"
