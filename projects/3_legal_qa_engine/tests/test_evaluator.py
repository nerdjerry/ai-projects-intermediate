"""
Tests for the LegalEvaluator.

This module contains unit tests for the ``LegalEvaluator`` class defined
in ``src/services/evaluator.py``. The tests cover:

    • **Perfect accuracy** — all predictions match ground truth.
    • **Zero accuracy** — no predictions match.
    • **Precision** — ratio of true positives to all positive predictions.
    • **Recall** — ratio of true positives to all actual positives.
    • **Edge cases** — empty inputs and mismatched list lengths.

**Testing best practices demonstrated here:**

• **Boundary-value testing:** Empty lists and single-element lists
  exercise edge cases that could cause division-by-zero errors.
• **Error-path testing:** ``test_length_mismatch_raises`` uses
  ``pytest.raises`` to verify that the evaluator fails loudly
  (with a descriptive ``ValueError``) rather than silently producing
  wrong results.
• **Deterministic inputs:** All test data is hardcoded, so tests are
  fast, repeatable, and require no external services.

**SOLID relevance:**
Because ``LegalEvaluator`` follows SRP (only evaluation), these tests
are self-contained — no mocking of LLM clients or HTTP layers needed.
"""
import pytest
from src.services.evaluator import LegalEvaluator


class TestLegalEvaluator:
    """Unit tests for LegalEvaluator.evaluate()."""

    def setup_method(self):
        """Create a fresh evaluator before each test (test isolation)."""
        self.evaluator = LegalEvaluator()

    def test_perfect_accuracy(self):
        """When all predictions match, accuracy should be 1.0."""
        preds = [{"risk_level": "high"}, {"risk_level": "low"}]
        truth = [{"risk_level": "high"}, {"risk_level": "low"}]
        result = self.evaluator.evaluate(preds, truth)
        assert result.accuracy == 1.0

    def test_zero_accuracy(self):
        """When no predictions match, accuracy should be 0.0."""
        preds = [{"risk_level": "high"}]
        truth = [{"risk_level": "low"}]
        result = self.evaluator.evaluate(preds, truth)
        assert result.accuracy == 0.0

    def test_risk_precision(self):
        """Precision = TP / (TP + FP). One correct + one false positive → 0.5."""
        preds = [{"risk_level": "high"}, {"risk_level": "high"}]
        truth = [{"risk_level": "high"}, {"risk_level": "low"}]
        result = self.evaluator.evaluate(preds, truth)
        assert result.risk_precision == 0.5

    def test_risk_recall(self):
        """Recall = TP / (TP + FN). One caught + one missed → 0.5."""
        preds = [{"risk_level": "low"}, {"risk_level": "high"}]
        truth = [{"risk_level": "high"}, {"risk_level": "high"}]
        result = self.evaluator.evaluate(preds, truth)
        assert result.risk_recall == 0.5

    def test_empty_inputs(self):
        """Empty lists should return zeroed-out metrics, not crash."""
        result = self.evaluator.evaluate([], [])
        assert result.accuracy == 0.0

    def test_length_mismatch_raises(self):
        """Mismatched list lengths should raise a clear ValueError."""
        preds = [{"risk_level": "high"}]
        truth = [{"risk_level": "high"}, {"risk_level": "low"}]
        with pytest.raises(ValueError, match="same length"):
            self.evaluator.evaluate(preds, truth)
